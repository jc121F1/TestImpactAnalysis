# [TestImpactAnalysis](https://github.com/jc121F1/TestImpactAnalysis)

This application provides Test Impact Analysis for Python projects that utilise the PyTest framework.

For command line instructions, use -h.

Setup and usage:

 1. Clone this repository into a folder of your choice within the project you wish to use this application with.
 
2. (Optional) Utilise virtualenv to create a virtual python environment
3. Use "pip install -r requirements.txt" to install the requirements stored in requirements.txt
4. Execute the setupcoverage.bat file from the root of your repository. This will create the correct settings for your coverage generation.
5. Execute the script using "python PATH/TO/test_impact_launcher.py --ARGS". Execute this from the root of your git repository.

If you wish to see how to utilise this script as part of a CI/CD workflow, see [this repository](https://github.com/jc121F1/TestRepository) for an example with GitHub Actions