Supported environments: Windows 10/11
The application will not function as expected on MacOS and has not been tested on Linux

Required external packages:
Pandas
Numpy
sv_ttk

pip install numpy
pip install pandas
pip install sv_ttk

The package includes a class, catalog, which can be called in two ways:
1. catalog(filename)
If the file directory is specified, the file will be read directly.
2. catalog()
If no information is specified, or the file cannot be found, the user will be prompted to open a file.
