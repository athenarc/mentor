import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Set, Dict, Any, Iterable

import pandas as pd
import streamlit as st

from benchmarking.totals import size_band_for

IGNORE_FIELDS = {
    'suite',
    'review_keys',
    'model_presets',
    'orchestrator_policy',
    'orchestrator_preset',
    'gold_label_policy',
    'leaderboard',
    'review_leaderboard',
    'runs.*.gold_label_policy_description',
    'runs.*.gatekeeper_model_label',
    'runs.*.gatekeeper_api_base',
    'runs.*.gatekeeper_api_key_source',
    'runs.*.orchestrator_model_label',
    'runs.*.orchestrator_api_base',
    'runs.*.orchestrator_api_key_source',
    'runs.*.screening_inspection_json',
    'runs.*.screening_inspection_markdown',
}

REQUIRED_FIELDS = {
    'generated_at',
    'runs',
    'runs.*.suite',
    'runs.*.gold_label_policy',
    'runs.*.n_studies',
    'runs.*.gold_pass_count',
    'runs.*.predicted_pass_count',
    'runs.*.screening_decision_count',
    'runs.*.parse_success',
    'runs.*.tp',
    'runs.*.fp',
    'runs.*.tn',
    'runs.*.fn',
    'runs.*.review_key',
    'runs.*.run_status',
    'runs.*.screening_completion_status',
    'runs.*.scored_for_aggregate',
    'runs.*.screening_attempt_count',
    'runs.*.rerun_triggered',
    'runs.*.duration_seconds',
    'runs.*.run_dir',
    'runs.*.gatekeeper_preset',
    'runs.*.gatekeeper_backend',
    'runs.*.gatekeeper_model_id',
    'runs.*.orchestrator_policy',
    'runs.*.orchestrator_preset',
    'runs.*.orchestrator_backend',
    'runs.*.orchestrator_model_id',

}

OPTIONAL_FIELDS = {
    'repeats',
    'runs.*.gold_exclude_count',
    'runs.*.predicted_exclude_count',
    'runs.*.missing_decision_count',
    'runs.*.duplicate_decision_count',
    'runs.*.invalid_decision_count',
    'runs.*.decision_coverage',
    'runs.*.accuracy',
    'runs.*.precision',
    'runs.*.recall',
    'runs.*.specificity',
    'runs.*.f1',
    'runs.*.benchmark_run_id',
    'runs.*.review_title',
    'runs.*.review_url',
    'runs.*.split',
    'runs.*.benchmark_architecture',
    'runs.*.run_index',
    'runs.*.error',
    'runs.*.incomplete_reason',
    'runs.*.orchestrator_step_count',
    'runs.*.gatekeeper_step_count',
    'runs.*.total_tokens',
    'runs.*.gatekeeper_input_tokens',
    'runs.*.orchestrator_input_tokens',
    'runs.*.gatekeeper_output_tokens',
    'runs.*.orchestrator_output_tokens'
}

LOGGER = logging.getLogger(__name__)


def parse_runs(runs: Iterable[Dict[str, Any]], context: Dict[str, Any] = None,
               _file_path: Path = None) -> Iterable[Dict[str, Any]]:
    logger = LOGGER
    fields_prefix = 'runs.*.'
    run_parse_index = 0
    for run in runs:
        fields = set(f'{fields_prefix}{f}' for f in run.keys())
        missing_fields = {f for f in REQUIRED_FIELDS if f.startswith(fields_prefix)} - fields
        if missing_fields:
            raise ValueError(f'Missing required fields: {", ".join(missing_fields)}')

        if context['repeats'] != 1 and 'run_index' not in run:
            raise KeyError('Multiple `repeats` are defined but no `run_index` definition is given')

        unexpected_fields = fields - (IGNORE_FIELDS | REQUIRED_FIELDS | OPTIONAL_FIELDS)
        if len(unexpected_fields) > 0:
            if _file_path:
                logger.warning(f'In file "{_file_path}": discovered the following unexpected fields: '
                               f'{", ".join(unexpected_fields)}.')
            else:
                logger.warning(f'Discovered the following unexpected fields: {", ".join(unexpected_fields)}.')

        flat_run = {
            k: v for k, v in run.items()
            if f'{fields_prefix}{k}' in REQUIRED_FIELDS | OPTIONAL_FIELDS and f'{fields_prefix}{k}' not in IGNORE_FIELDS
        }
        flat_run['benchmark_architecture'] = run.get('benchmark_architecture', 'batch_orchestrator_v1')
        flat_run['balance'] = flat_run['gold_pass_count'] / flat_run['n_studies']
        flat_run['size_band'] = size_band_for(flat_run['n_studies'])['key']

        yield flat_run
        # flat_run = {
        #     'experiment_recorded_at': context['generated_at'],
        #     'suite': run['suite'],
        #     'gold_label_policy': run['gold_label_policy'],
        #     'n_studies': run['n_studies'],
        #     'gold_pass_count': run['gold_pass_count'],
        #     'predicted_pass_count': run['predicted_pass_count'],
        #     'screening_decision_count': run['screening_decision_count'],
        #     'parse_success': run['parse_success'],
        #     'tp': run['tp'],
        #     'fp': run['fp'],
        #     'tn': run['tn'],
        #     'fn': run['fn'],
        #     'review_key': run['review_key'],
        #     'run_status': run['run_status'],
        #     'screening_completion_status': run['screening_completion_status'],
        #     'scored_for_aggregate': run['scored_for_aggregate'],
        #     'screening_attempt_count': run['screening_attempt_count'],
        #     'rerun_triggered': run['rerun_triggered'],
        #     'duration_seconds': run['duration_seconds'],
        #     'run_dir': Path(run['run_dir']).resolve().absolute(),
        #     'gatekeeper_preset': run['gatekeeper_preset'],
        #     'gatekeeper_backend': run['gatekeeper_backend'],
        #     'gatekeeper_model_id': run['gatekeeper_model_id'],
        #     'orchestrator_policy': run['orchestrator_policy'],
        #     'orchestrator_preset': run['orchestrator_preset'],
        #     'orchestrator_backend': run['orchestrator_backend'],
        #     'orchestrator_model_id': run['orchestrator_model_id'],
        #     'repeats': context['repeats'],
        #     'error': run.get('error'),
        #     'incomplete_reason': run.get('incomplete_reason'),
        #     'missing_decision_count': run.get('missing_decision_count', 0),
        #     'duplicate_decision_count': run.get('duplicate_decision_count', 0),
        #     'invalid_decision_count': run.get('invalid_decision_count', 0),
        #     'review_title': run.get('review_title'),
        #     'review_url': run.get('review_url'),
        #     'split': run.get('split'),
        #     'run_index': run.get('run_index', 1),
        #     'benchmark_run_descriptor': run.get('benchmark_run_id'),
        #     'benchmark_architecture': run.get('benchmark_architecture', 'batch_architecture_v1'),
        # }
        #
        # gold_exclude_count = run.get('gold_exclude_count')
        # if not gold_exclude_count and (not run['n_studies'] or not run['gold_pass_count']):
        #     raise ValueError('Missing field `gold_exclude_count` cannot be inferred because either `n_studies` or '
        #                      '`gold_pass_count` fields are `None`.')
        #
        #
        # flat_run = {
        #     **flat_run,
        #     'gold_exclude_count': run.get(
        #         'gold_exclude_count', run['n_studies'] - run['gold_pass_count']
        #     ),
        #     'predicted_exclude_count': run.get(
        #         'predicted_exclude_count', run['n_studies'] - run['predicted_pass_count']
        #     ),
        #     'decision_coverage': run.get(
        #         'decision_coverage',
        #         1 - (run['missing_decision_count'] / run['n_studies']) if run['n_studies'] != 0 else None
        #     ),
        #     'accuracy': run.get(
        #         'accuracy',
        #         (run['tp'] + run['tn']) / (run['tp'] + run['tn'] + run['fp'] + run['fn'])
        #         if run['tp'] + run['tn'] + run['fp'] + run['fn'] != 0 else 0
        #     ),
        #     'precision': run.get(
        #         'precision',
        #         run['tp'] / (run['tp'] + run['fp']) if run['tp'] + run['fp'] != 0 else 0
        #     ),
        #     'recall': run.get(
        #         'recall',
        #         run['tp'] / (run['fn'] + run['tp']) if run['fn'] + run['tp'] != 0 else 0
        #     ),
        #     'specificity': run.get(
        #         'specificity',
        #         run['tn'] / (run['fp'] + run['tn']) if run['fp'] + run['tn'] != 0 else 0
        #     ),
        # }
        #
        # flat_run['f1'] = run.get(
        #     'f1',
        #     2 * flat_run['precision'] * flat_run['recall'] / (flat_run['precision'] + flat_run['recall'])
        #     if flat_run['precision'] + flat_run['recall'] != 0 else 0
        # )
        #
        # flat_run['experiment_id'] = '_'.join([
        #     flat_run['orchestrator_policy'],
        #     flat_run['orchestrator_model_id'],
        #     flat_run['gatekeeper_model_id'],
        #     flat_run['suite'],
        #     flat_run['benchmark_architecture'],
        #     flat_run['gold_label_policy'],
        #     flat_run['experiment_recorded_at'].strftime('%Y%m%d%H%M%S%f')
        # ])
        # flat_run['run_id'] = '_'.join([
        #     flat_run['review_key'],
        #     str(flat_run['run_index'])
        # ])


def parse_summary_dict(summary_dict: Dict[str, Any], _file_path: Path = None) -> Iterable[Dict[str, Any]]:
    logger = LOGGER
    fields = set(summary_dict.keys())

    missing_fields = {f for f in REQUIRED_FIELDS if '.' not in f} - fields
    if missing_fields:
        raise ValueError(f'Missing required fields: {", ".join(missing_fields)}')

    unexpected_fields = fields - (IGNORE_FIELDS | REQUIRED_FIELDS | OPTIONAL_FIELDS)
    if len(unexpected_fields) > 0:
        if _file_path:
            logger.warning(f'In file "{_file_path}": discovered the following unexpected fields: '
                           f'{", ".join(unexpected_fields)}.')
        else:
            logger.warning(f'Discovered the following unexpected fields: {", ".join(unexpected_fields)}.')

    generated_at = datetime.fromisoformat(summary_dict['generated_at'])
    repeats = summary_dict.get('repeats', 1)

    for run in parse_runs(summary_dict['runs'], context={'repeats': repeats, 'generated_at': generated_at},
                          _file_path=_file_path):
        yield run


@st.cache_data
def load_data(
        benchmark_results_dir: Path, gold_label_policies: Set[str] = None,
        architectures: Set[str] = None, experiments: Set[str] = None,
        models: Set[str] = None, keep_completed: bool = False
) -> pd.DataFrame:
    logger = LOGGER

    summary_jsons = benchmark_results_dir.glob('*/*/summary.json')

    if experiments:
        summary_jsons = [p for p in summary_jsons if p.parts[0].strip() not in experiments]
    logger.info('Loading data...')
    all_runs_df = None
    for p in summary_jsons:
        with open(p, encoding='utf-8') as f:
            summary_json_content = json.load(f)
        experiment_runs = list(parse_summary_dict(summary_json_content, _file_path=p))
        experiment_runs_df = pd.DataFrame(experiment_runs)
        if all_runs_df is None:
            all_runs_df = experiment_runs_df
        else:
            all_runs_df = pd.concat([all_runs_df, experiment_runs_df])
    # all_runs_df = pd.DataFrame([parse_summary_dict(json.load(open(p, encoding='utf-8'))) for p in summary_jsons])
    logger.info(f'Loaded data for {all_runs_df.shape[0]} discovered runs')

    logger.info('Calculating filters...')
    policy_mask = all_runs_df['gold_label_policy'].apply(lambda p: p in gold_label_policies) if gold_label_policies \
        else pd.Series(True, index=all_runs_df.index)
    architectures_mask = all_runs_df['architecture'].isin(architectures) if architectures \
        else pd.Series(True, index=all_runs_df.index)
    models_mask = all_runs_df['gatekeeper_preset'].isin(models) if models \
        else pd.Series(True, index=all_runs_df.index)
    completed_mask = (
            (all_runs_df['parse_success']) & (all_runs_df['screening_completion_status'] == 'complete')
    ) if keep_completed else pd.Series(True, index=all_runs_df.index)
    logger.info('Applying filters...')
    result = all_runs_df[policy_mask & architectures_mask & models_mask & completed_mask].reset_index(drop=True)
    logger.info(f'Final number of filtered runs: {result.shape[0]}')

    return result

# if __name__ == '__main__':
#     parser = ArgumentParser()
#     parser.add_argument('benchmark_results_dir', type=Path)
#     parser.add_argument(
#         '--architectures',
#         choices=list(EXPERIMENT_ARCHITECTURE_LABEL_TO_VALUE_INDEX.keys()),
#         nargs='+',
#     )
#     parser.add_argument(
#         '--gold-label-policies',
#         choices=list(GOLD_LABEL_POLICY_LABEL_TO_VALUE_INDEX.keys()),
#         nargs='+',
#     )
#     parser.add_argument(
#         '--logging-level',
#         choices=list(range(len(LOGGING_LEVEL))),
#         type=int
#     )
#     parser.add_argument(
#         '--models',
#         choices=list(MODEL_LABEL_TO_VALUE_INDEX.keys()),
#         nargs='+',
#         help='Explicit definition of models for which to collect the performed runs results. If used, only runs of '
#              'models defined with this argument will be collected, excluding the runs ran with models potentially '
#              'defined with `--ignore-models`.'
#     )
#     parser.add_argument(
#         '--ignore-models',
#         choices=list(MODEL_LABEL_TO_VALUE_INDEX.keys()),
#         nargs='+',
#         help='Definition of models for which to ignore the respective runs.'
#     )
#     # parser.add_argument(
#     #     '--experiments',
#     #     nargs='+',
#     #     help='Explicit definition of experiment directory names for which to collect the performed runs results. If '
#     #          'used, only runs contained within the named directories will be collected, excluding any runs contained '
#     #          'within experiment directories named with `--exclude-experiments`.'
#     # )
#     # parser.add_argument(
#     #     '--ignore-experiments',
#     #     nargs='+',
#     #     help='Definition of experiment directories for which to ignore the respective runs.'
#     # )
#
#     args = parser.parse_args()
#
#     internal_logging_level = LOGGING_LEVEL[args.logging_level]
#     setup_logger(LOGGER, internal_logging_level)
#
#     architectures = set(
#         EXPERIMENT_ARCHITECTURE_LABEL_TO_VALUE_INDEX[a] for a in args.architectures
#     ) if args.architectures else set()
#     gold_label_policies = set(
#         GOLD_LABEL_POLICY_LABEL_TO_VALUE_INDEX[p] for p in args.gold_label_policies
#     ) if args.gold_label_policies else set()
#
#     explicit_models = set(args.models) if args.models else set(MODEL_LABEL_TO_VALUE_INDEX.keys())
#     ignore_models = set(args.ignore_models) if args.ignore_models else set()
#     models = explicit_models - ignore_models
#
#     # explicit_experiments = set(args.experiments) if args.experiments else set()
#     # ignore_experiments = set(args.ignore_experiments) if args.ignore_experiments else set()
#     # experiments = explicit_experiments - ignore_experiments
#
#     LOGGER.debug(
#         'Will collect runs with the following attributes\n'
#         f'- Architecture: {"*" if not architectures else ", ".join(str(a) for a in architectures)}\n'
#         f'- Gold label policies: {"*" if not gold_label_policies else ", ".join(str(p) for p in gold_label_policies)}\n'
#         f'- Models: {"*" if not models else ", ".join(str(m) for m in models)}'
#         # f'- Experiments: {"*" if not experiments else ", ".join(str(e) for e in experiments)}'
#     )
#
#     load_data(
#         args.benchmark_results_dir.expanduser().resolve().absolute(),
#         architectures=architectures,
#         gold_label_policies=gold_label_policies,
#         models=models
#     )
