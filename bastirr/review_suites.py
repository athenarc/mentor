import argparse
import json
import logging
import re
import sys
from collections.abc import Set as AbstractSet
from datetime import datetime
from enum import StrEnum
from typing import Sequence, Iterable

import numpy as np
import pandas as pd

from bastirr.config import DATASET_FILES, BASTIRR_DIR
from bastirr.logging_utils import LoggingLevel, LOGGING_LEVEL_MAP, setup_tool_logger

_DOI_PATTERN = re.compile(r"(?<=^https://www\.cochranelibrary\.com/cdsr/doi/10\.1002/)[\w.]+(?=/full$)")
_LOGGER = logging.getLogger(__name__)


class Subcommands(StrEnum):
    SAMPLE = 'sample'


class SamplingStrategy(StrEnum):
    RANDOM = 'random'
    TOP = 'top'


class GoldLabelPolicy(StrEnum):
    INCLUDE = 'include'
    EXCLUDE = 'exclude'


class BinSamplingPolicy(StrEnum):
    PROPORTIONAL = 'proportional'
    SYMMETRIC = 'symmetric'


def _get_id_from_review_url(review_url: str) -> str:
    _LOGGER.debug(f'Trying to match pattern `{_DOI_PATTERN}` against review URL {review_url}...')
    m = re.search(_DOI_PATTERN, review_url)
    if m is None:
        raise ValueError(f'Unexpected URL format: {review_url}, cannot infer ID')
    doi_segment = m.group(0)
    _LOGGER.debug(f'Matched DOI segment "{doi_segment}.')
    return doi_segment.lower().replace('.', '_')


def _retrieve_reviews(splits: AbstractSet[str] = None,
                      gold_label_policy: GoldLabelPolicy = GoldLabelPolicy.EXCLUDE) -> pd.DataFrame:
    if splits is None:
        splits = set(DATASET_FILES.keys())

    _LOGGER.debug('Validating specified splits...')
    invalid_splits = splits - set(DATASET_FILES.keys())
    if invalid_splits:
        raise ValueError(f'Invalid split specified: {next(iter(invalid_splits))}')

    _LOGGER.debug('Determining gold label normalization...')
    # This is the correct one but current backend is fixed on validating ALWAYS based on include policy.
    # This should be re-enabled when validation logic is fixed.
    # gold_label_normalization = np.floor if gold_label_policy == GoldLabelPolicy.EXCLUDE else np.ceil
    gold_label_normalization = np.ceil

    reviews_dfs = list()
    for split in sorted(splits):
        _LOGGER.debug(f'Reading data for split `{split}`...')
        split_df = pd.read_csv(DATASET_FILES[split])
        _LOGGER.debug(f'Read {split_df.shape[0]} rows from {DATASET_FILES[split]}.')
        _LOGGER.debug(f'Applying gold label normalization...')
        split_df['Gold_Label'] = split_df['label'].apply(gold_label_normalization)
        _LOGGER.debug('Aggregating data for each review...')
        reviews_df = split_df.groupby('Review_URL', as_index=False).agg(
            review_url=('Review_URL', 'first'),
            title=('Review_Title', 'first'),
            expected_n_studies=('Review_URL', 'size'),
            expected_n_screen_pass=('Gold_Label', lambda s: (s == 1).sum()),
            expected_n_screen_exclude=('Gold_Label', lambda s: (s == 0).sum())
        )
        _LOGGER.debug(f'Computed review aggregates for {reviews_df.shape[0]} rows.')
        _LOGGER.debug(f'Calculating keys for reviews...')
        reviews_df['key'] = reviews_df['review_url'].apply(_get_id_from_review_url)
        _LOGGER.debug(f'Annotating reviews with corresponding split value...')
        reviews_df['split'] = split
        reviews_dfs.append(reviews_df)
        _LOGGER.debug(f'-' * 40)

    _LOGGER.debug('Joining and returning split reviews\'s data...')
    return pd.concat(reviews_dfs, ignore_index=True)


def _filter_reviews(reviews_df: pd.DataFrame, min_studies: int = None, max_studies: int = None,
                    min_balance: float = None,
                    max_balance: float = None) -> pd.DataFrame:
    if min_studies is None:
        min_studies = 0
        _LOGGER.debug(f'Minimum studies filter value inferred as {min_studies}.')
    elif min_studies < 0:
        raise ValueError('Minimum number of studies must be either 0 or positive.')
    else:
        _LOGGER.debug(f'Minimum studies filter value specified as {min_studies}.')

    if max_studies is None:
        max_studies = reviews_df['expected_n_studies'].max()
        _LOGGER.debug(f'Maximum studies filter value inferred as {max_studies}.')
    elif max_studies < 0:
        raise ValueError('Maximum number of studies must be either 0 or positive.')
    else:
        _LOGGER.debug(f'Maximum studies filter value specified as {max_studies}.')

    if min_balance is None:
        min_balance = 0.0
        _LOGGER.debug(f'Minimum balance filter value inferred as {min_balance}.')
    elif min_balance < 0:
        raise ValueError(f'Invalid minimum balance specified: {min_balance}. '
                         f'Balance must be any number between 0 and 1.')
    else:
        _LOGGER.debug(f'Minimum balance filter value specified as {min_balance}.')

    if max_balance is None:
        max_balance = 1.0
        _LOGGER.debug(f'Maximum balance filter value inferred as {max_balance}.')
    elif max_balance < 0:
        raise ValueError(f'Invalid maximum balance specified: {max_balance}. '
                         f'Balance must be any number between 0 and 1.')
    else:
        _LOGGER.debug(f'Maximum balance filter value specified as {max_balance}.')

    temp_df = reviews_df.copy()
    _LOGGER.debug(f'Calculating reviews\' balance...')
    temp_df['balance'] = temp_df['expected_n_screen_pass'] / temp_df['expected_n_studies']
    _LOGGER.debug(f'Applying filters...')
    filtered_reviews_df = reviews_df[
        reviews_df['expected_n_studies'].between(min_studies, max_studies, inclusive='both') &
        (
                reviews_df['expected_n_screen_pass'] / reviews_df['expected_n_studies']
        ).between(min_balance, max_balance, inclusive='both')
        ]
    _LOGGER.debug(f'Filter application resulted in {filtered_reviews_df.shape[0]} rows.')

    return filtered_reviews_df


def _sample_reviews(reviews_df: pd.DataFrame, sample_sizes: Sequence[int], bin_breakpoints: AbstractSet[int] = None,
                    bin_sampling_policy: BinSamplingPolicy = BinSamplingPolicy.PROPORTIONAL, seed: int = None):
    if bin_breakpoints is None:
        bin_breakpoints = list()
    _LOGGER.debug(f'Validating sampling configuration...')
    if len(sample_sizes) != len(bin_breakpoints) + 1 and len(sample_sizes) != 1:
        raise ValueError(f'Invalid sample sizes defined ({" ,".join(str(s) for s in sample_sizes)}) for '
                         f'{len(bin_breakpoints) + 1} bins. Either 1 or {len(bin_breakpoints) + 1} sample sizes should '
                         f'be specified.')

    _LOGGER.debug(f'Validating sampling sizes\' values...')
    negative_sample_sizes = [s for s in sample_sizes if s < 0]
    if negative_sample_sizes:
        raise ValueError(f'Negative sample size was given: {negative_sample_sizes[0]}. Sample sizes must be positive '
                         f'or 0')

    _LOGGER.debug(f'Sorting bin breakpoints')
    sorted_bin_breakpoints = sorted(bin_breakpoints)

    min_studies = reviews_df['expected_n_studies'].min()
    max_studies = reviews_df['expected_n_studies'].max()

    _LOGGER.debug(f'Composing bin edges')
    bin_edges = sorted([min_studies, *sorted_bin_breakpoints, max_studies+1])

    _LOGGER.debug(f'Distributing reviews to bins based on number of studies...')
    reviews_df['bin_interval'] = pd.cut(reviews_df['expected_n_studies'], bin_edges, right=False)

    bin_samples = list()
    bin_idx = 0
    for interval, bin in reviews_df.groupby('bin_interval'):
        _LOGGER.debug(f'Evaluating sampling for bin [{interval.left}, {interval.right})...')
        _LOGGER.debug(f'Determining sampling size...')
        if len(sample_sizes) == len(bin_breakpoints) + 1:
            subsample_size = sample_sizes[bin_idx]
            _LOGGER.debug(f'Explicit sampling size for bin specified as {subsample_size}.')
        else:
            if bin_sampling_policy == BinSamplingPolicy.PROPORTIONAL:
                subsample_size = int((sample_sizes[0] * bin.shape[0]) / reviews_df.shape[0])
                _LOGGER.debug(f'Calculated sampling size based on proportional policy as {subsample_size}')
            else:
                subsample_size = int(sample_sizes[0] / (len(bin_breakpoints) + 1))
                _LOGGER.debug(f'Calculated sampling size based on symmetric policy as {subsample_size}')
        _LOGGER.debug(f'Attempting to retrieve a sample of {subsample_size} reviews from a bin of {bin.shape[0]} '
                      f'reviews...')
        bin_sample = bin.sample(subsample_size, random_state=seed)
        _LOGGER.debug(f'Retrieved {bin_sample.shape[0]} reviews')
        bin_samples.append(
            bin_sample
        )
        _LOGGER.debug(f'-' * 40)
        bin_idx += 1
    _LOGGER.debug(f'Joining and returning bin samples\' data')
    return pd.concat(bin_samples)


def _top_reviews(reviews_df: pd.DataFrame, sample_sizes: Sequence[int], bin_breakpoints: AbstractSet[int] = None,
                    bin_sampling_policy: BinSamplingPolicy = BinSamplingPolicy.PROPORTIONAL):
    if bin_breakpoints is None:
        bin_breakpoints = list()
    _LOGGER.debug(f'Validating sampling configuration...')
    if len(sample_sizes) != len(bin_breakpoints) + 1 and len(sample_sizes) != 1:
        raise ValueError(f'Invalid sample sizes defined ({" ,".join(str(s) for s in sample_sizes)}) for '
                         f'{len(bin_breakpoints) + 1} bins. Either 1 or {len(bin_breakpoints) + 1} sample sizes should '
                         f'be specified.')

    _LOGGER.debug(f'Validating sampling sizes\' values...')
    negative_sample_sizes = [s for s in sample_sizes if s < 0]
    if negative_sample_sizes:
        raise ValueError(f'Negative sample size was given: {negative_sample_sizes[0]}. Sample sizes must be positive '
                         f'or 0')

    _LOGGER.debug(f'Sorting bin breakpoints')
    sorted_bin_breakpoints = sorted(bin_breakpoints)

    min_studies = reviews_df['expected_n_studies'].min()
    max_studies = reviews_df['expected_n_studies'].max()

    _LOGGER.debug(f'Composing bin edges')
    bin_edges = sorted([min_studies, *sorted_bin_breakpoints, max_studies+1])

    _LOGGER.debug(f'Distributing reviews to bins based on number of studies...')
    reviews_df['bin_interval'] = pd.cut(reviews_df['expected_n_studies'], bin_edges, right=False)

    bin_samples = list()
    bin_idx = 0
    for interval, bin in reviews_df.groupby('bin_interval'):
        _LOGGER.debug(f'Evaluating sampling for bin [{interval.left}, {interval.right})...')
        _LOGGER.debug(f'Determining sampling size...')
        if len(sample_sizes) == len(bin_breakpoints) + 1:
            subsample_size = sample_sizes[bin_idx]
            _LOGGER.debug(f'Explicit sampling size for bin specified as {subsample_size}.')
        else:
            if bin_sampling_policy == BinSamplingPolicy.PROPORTIONAL:
                subsample_size = int((sample_sizes[0] * bin.shape[0]) / reviews_df.shape[0])
                _LOGGER.debug(f'Calculated sampling size based on proportional policy as {subsample_size}')
            else:
                subsample_size = int(sample_sizes[0] / (len(bin_breakpoints) + 1))
                _LOGGER.debug(f'Calculated sampling size based on symmetric policy as {subsample_size}')
        _LOGGER.debug(f'Attempting to retrieve a sample of {subsample_size} reviews from a bin of {bin.shape[0]} '
                      f'reviews...')
        bin_sample = bin[:subsample_size]
        _LOGGER.debug(f'Retrieved {bin_sample.shape[0]} reviews')
        bin_samples.append(
            bin_sample
        )
        _LOGGER.debug(f'-' * 40)
        bin_idx += 1
    _LOGGER.debug(f'Joining and returning bin samples\' data')
    return pd.concat(bin_samples)

def _append_to_canonical_suites(reviews_df: pd.DataFrame, name: str = None, description: str = ''):
    if name is None:
        _LOGGER.debug(f'Inferring canonical suite name as current local timestamp...')
        name = datetime.now().astimezone().strftime('%Y%m%d%H%M%S')
        _LOGGER.debug(f'Inferred canonical suite name: {name}')
    else:
        _LOGGER.debug(f'Using specified name for canonical suite: {name}')

    _LOGGER.debug(f'Composing canonical suite data...')
    suite_data = {
        'name': name,
        'description': description,
        'reviews': reviews_df[
            ['key', 'split', 'review_url', 'title', 'expected_n_studies', 'expected_n_screen_pass',
             'expected_n_screen_exclude']
        ].to_dict(orient='records')
    }
    _LOGGER.debug(f'Composed canonical suite data:\n{json.dumps(suite_data, indent=2)}.')

    canonical_suites_json = BASTIRR_DIR / 'benchmarking' / 'config' / 'review_suites.json'
    _LOGGER.debug(f'Reading existing canonical suites data from {canonical_suites_json}...')
    with open(canonical_suites_json, encoding='utf-8') as fin:
        canonical_suites = json.load(fin)

    canonical_suites_list = canonical_suites['canonical_suites']
    canonical_suites_list.append(suite_data)

    _LOGGER.debug(f'Writing new canonical suites data to {canonical_suites_json}...')
    with open(canonical_suites_json, 'w', encoding='utf-8') as fout:
        json.dump(canonical_suites, fout, indent=2)


def generate_suite(*sample_sizes: int, splits: AbstractSet[str] = None, min_studies: int = None,
                   max_studies: int = None, min_balance: float = None, max_balance: float = None,
                   bin_breakpoints: AbstractSet[int] = None, name: str = None, description: str = '',
                   bin_sampling_policy: BinSamplingPolicy = BinSamplingPolicy.PROPORTIONAL,
                   gold_label_policy: GoldLabelPolicy = GoldLabelPolicy.EXCLUDE, seed: int = None) -> pd.DataFrame:
                   gold_label_policy: GoldLabelPolicy = GoldLabelPolicy.EXCLUDE, seed: int = None,
                   strategy: SamplingStrategy = SamplingStrategy.RANDOM) -> pd.DataFrame:
    _LOGGER.info(f'Loading reviews...')
    retrieved_reviews_df = _retrieve_reviews(splits=splits, gold_label_policy=gold_label_policy)
    _LOGGER.info(f'Loaded {retrieved_reviews_df.shape[0]} reviews.')
    _LOGGER.info(f'Filtering reviews...')
    filtered_reviews_df = _filter_reviews(retrieved_reviews_df, min_studies=min_studies, max_studies=max_studies,
                                          min_balance=min_balance, max_balance=max_balance)
    _LOGGER.info(f'Retained {filtered_reviews_df.shape[0]} reviews after filtering.')
    _LOGGER.info(f'Sampling reviews...')
    match strategy:
        case SamplingStrategy.RANDOM:
            sampled_reviews_df = _sample_reviews(
                sorted_reviews_df, sample_sizes, bin_breakpoints=bin_breakpoints,
                bin_sampling_policy=bin_sampling_policy, seed=seed)
        case SamplingStrategy.TOP:
            sampled_reviews_df = _top_reviews(
                sorted_reviews_df, sample_sizes, bin_breakpoints=bin_breakpoints,
                bin_sampling_policy=bin_sampling_policy,
            )
    _LOGGER.info(f'Sampled {sampled_reviews_df.shape[0]} reviews.')
    _LOGGER.info(f'Appending generated suite to canonical suites JSON...')
    _append_to_canonical_suites(sampled_reviews_df, name=name, description=description)
    _LOGGER.info(f'Appended generated suite to canonical suites JSON.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Auxiliary script for generating suites of reviews which can be used by the isolated gatekeeper '
                    'benchmarking pipeline.'
    )
    subparsers = parser.add_subparsers(dest='command', required=True)
    sample_parser = subparsers.add_parser(Subcommands.SAMPLE)
    sample_parser.add_argument(
        '--name',
        help='Unique name of the generated suite. If not defined, name will be generated using the current date and '
             'time.'
    )
    sample_parser.add_argument(
        '--description',
        help='Optional description of the generated suite.'
    )
    sample_parser.add_argument(
        '-N', '--sample-sizes',
        type=int,
        nargs='+',
        default=[5],
        help='Number of systematic reviews to randomly sample. If one value is given then it corresponds to the sample '
             'size after applying filtering. If one value is given and at least one bin breakpoint is defined, this '
             'value will be distributed across the bins, proportionally to the bin size. If multiple values are given, '
             'then these should map to the bins inferred by the defined breakpoints and correspond to the per-bin '
             'subsample size.'
    )
    sample_parser.add_argument(
        '--splits',
        nargs='+',
        choices=list(DATASET_FILES.keys()),
        help='Names of systematic review split sets to sample from.'
    )
    sample_parser.add_argument(
        '--min-studies',
        type=int,
        help='Minimum number of studies that sampled reviews should have.'
    )
    sample_parser.add_argument(
        '--max-studies',
        type=int,
        help='Maximum number of studies that sampled reviews should have.'
    )
    sample_parser.add_argument(
        '--min-balance',
        type=int,
        help='Minimum balance that evaluated reviews should have.'
    )
    sample_parser.add_argument(
        '--max-balance',
        type=int,
        help='Maximum balance that evaluated reviews should have.'
    )
    sample_parser.add_argument(
        '--bin-breakpoints',
        type=int,
        nargs='+',
        help='Breakpoints that correspond to the number of studies that will be used as reference for constructing '
             'bins between the computed `min_studies` and `max_studies`, after filtering. For example, assuming '
             '`min_studies=10` and `max_studies=40`, given `--bin-breakpoints 15 25 30`, reviews will be distributed, '
             'after filtering, in the following four bins: [10,15), [15, 25), [25,30) and [30, 40).'
    )
    sample_parser.add_argument(
        '--logging-level',
        choices=list(LoggingLevel),
        default=LoggingLevel.INFO,
        type=LoggingLevel,
        help='Logging level of the script.'
    )
    sample_parser.add_argument(
        '--gold-label-policy',
        choices=list(GoldLabelPolicy),
        type=GoldLabelPolicy,
        default=GoldLabelPolicy.EXCLUDE,
        help='Gold label policy based on which to calculate the expected included and excluded studies during '
             'screening.'
    )
    sample_parser.add_argument(
        '--bin-sampling-policy',
        type=BinSamplingPolicy,
        choices=list(BinSamplingPolicy),
        default=BinSamplingPolicy.PROPORTIONAL,
        help='Sampling policy when using bins with no fixed bin sample size. In `proportional` policy, an analogous '
             'amount of reviews will be sampled from each bin, based on the bin\'s review size. In `symmetric` policy, '
             'the number of reviews which will be sampled from each bin will be the same. In both policies the number '
             'of reviews to sample is calculated based on the final calculated sample size, after applying filtering.'
    )
    sample_parser.add_argument(
        '--seed',
        type=int,
        help='An integer value for fixing sampling randomness, in favor of reproducibility.'
    )
    sample_parser.add_argument(
        '--strategy',
        type=SamplingStrategy,
        default=SamplingStrategy.RANDOM,
        help='Strategy based on which to generate samples.'
    )

    parsed_args = vars(parser.parse_args())

    setup_tool_logger(_LOGGER, LOGGING_LEVEL_MAP[parsed_args.pop('logging_level')])

    command = parsed_args.pop('command')

    if command == Subcommands.SAMPLE:
        sample_sizes = parsed_args.pop('sample_sizes')
        try:
            generate_suite(*sample_sizes, **parsed_args)
        except Exception as e:
            _LOGGER.critical(e)
            sys.exit(1)
