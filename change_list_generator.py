from git import Repo, Commit, Diff
from pathlib import Path



class ChangeListGenerator:
    def __init__(self, path : Path):

        self.repo = Repo(path)


    def get_changelist(self, initial_commit_id, final_commit_id):
        try:
            init_commit = self.repo.commit(initial_commit_id)
            print(f"Selecting init_commit as : {init_commit}")
            final_commit = self.repo.commit(final_commit_id)
            print(f"Selecting final commit as : {final_commit}")
        except Exception as e:
            print("An exception occured, it is as follows:  {e}")

        diff = final_commit.diff(init_commit)
        
        return diff

    
c = ChangeListGenerator(Path("C:\\Users\\jackc\Desktop\\TestImpactAnalysis"))

print(c.get_changelist("HEAD~1","main"))
