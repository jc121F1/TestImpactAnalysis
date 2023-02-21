from abc import ABC, abstractmethod
from collections import namedtuple

class BaseChangeListGenerator(ABC):
    """
        This class is used to generate a changelist that we will use to select tests.
    """

    @abstractmethod
    def __init__(self):
        """
           Creates a ChangeListGenerator object.
        """

    @abstractmethod
    def get_changelist(self, init_id, final_id):
        """
            Generates a changelist between two commits. Initial revision/commit id must be the ancestor of the final revision/commit id (that is, comes before in our tree of commits)

            Returns a list of files that have changed as well as what type of change was made and the path to that file.
        """
        pass

    
ChangeInfo = namedtuple("ChangeInfo", ["path","change_type"])