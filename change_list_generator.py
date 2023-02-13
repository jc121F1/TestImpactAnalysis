from git import Repo, Commit, Diff, GitError, NoSuchPathError, InvalidGitRepositoryError, GitCommandError
from pathlib import Path

class ChangeListGenerator:
    """
        This class is used to generate git.Diff objects that represent the changelist between two commits.
        It takes a repo as an argument upon creation.
    """

    def __init__(self, path: Path):
        """
           Creates a ChangeListGenerator object.

        Args:
            path (Path): Local path to the git repository that we want to build a changelist in.
        """
        try:
            self.repo = Repo(path)
        except (NoSuchPathError, InvalidGitRepositoryError) as e:
            print("An exception occured, it is as follows:  {e}")
            raise e

    def get_changelist(self, initial_commit_id, final_commit_id):
        """
            Generates the Diff object between two commits. Initial commit must be the ancestor of the final commit (that is, comes before in our tree of commits)

        Args:
            initial_commit_id (str): Commit id for the first commit we want to compare
            final_commit_id (str): Commit id for the second commit we want to compare.

        Raises:
            ValueError: If initial commit is not an ancestor of final commit, this error will be raised.

        Returns:
            git.DiffIndex : The diff between the initial and final commit, containing all changes and their types in an iterable.
        """
        try:
            if self.initial_commit_is_before_final_commit(initial_commit_id, final_commit_id):

                init_commit = self.repo.commit(initial_commit_id)
                print(f"Selecting init_commit as : {init_commit}")
                final_commit = self.repo.commit(final_commit_id)
                print(f"Selecting final commit as : {final_commit}")
                diff = final_commit.diff(init_commit)

                return diff
            else:
                raise ValueError(
                    "Initial commit occurs after final commit. This is an invalid configuration for generating a changelist.")
        except (Exception, GitCommandError) as e:
            print(f"An exception occured, it is as follows:  {e}")
            raise e

    def initial_commit_is_before_final_commit(self, initial_commit_id, final_commit_id):
        """
            Returns whether the commit referred to by initial_commit_id is an ancestor of final_commit_id

        Args:
            initial_commit_id (str): Commit id for the first commit we want to compare
            final_commit_id (str): Commit id for the second commit we want to compare.

        Returns:
            Bool: Is the commit referred to by initial_commit_id is an ancestor of final_commit_id, true or false.
        """
        return self.repo.is_ancestor(initial_commit_id, final_commit_id)
    
    def __del__(self):
        self.repo.close()
