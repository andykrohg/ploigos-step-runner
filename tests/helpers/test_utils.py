import os
import yaml

from git import Repo

from tssc import TSSCFactory


def create_git_commit_with_sample_file(temp_dir, git_repo, sample_file_name = 'sample-file', commit_message = 'test'):
    sample_file = os.path.join(temp_dir.path, sample_file_name)
    open(sample_file, 'wb').close()
    git_repo.index.add([sample_file])
    git_repo.index.commit(commit_message)

def create_temp_git_repo(working_dir_path):
    repo = Repo.init(working_dir_path)
    repo.index.add(working_dir_path)
    repo.index.commit("initial commit")

def run_step_generate_metadata_for_tests(temp_dir, config, runtime_args=None):

    create_temp_git_repo(temp_dir.path)
    results_dir_path = os.path.join(temp_dir.path, 'tssc-results')

    factory = TSSCFactory(config, results_dir_path)
    if runtime_args:
        factory.run_step('generate-metadata', runtime_args)
    else:
        factory.run_step('generate-metadata')

def run_step_test_with_result_validation(temp_dir, step_name, config, expected_step_results, runtime_args=None):
    results_dir_path = os.path.join(temp_dir.path, 'tssc-results')

    factory = TSSCFactory(config, results_dir_path)
    if runtime_args:
        factory.run_step(step_name, runtime_args)
    else:
        factory.run_step(step_name)

    results_file_name = "tssc-results.yml"
    with open(os.path.join(results_dir_path, results_file_name), 'r') as step_results_file:
        actual_step_results = yaml.safe_load(step_results_file.read())
        assert actual_step_results == expected_step_results
