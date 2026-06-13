
class SebaParser:

    __filename__ = None
    __file_content__ = None
    
    __seba_name__ = None
    __control_file_name__ = None
    __testbench_file_name__ = None
    __corners_gen_file_name__ = None
    __script_file_name__ = None
    __plot_file_name__ = None
    __extraction_names__ = None

    @classmethod
    def parse(cls, filename):
        cls.__filename__ = filename

        file_content = None

        with open(filename, "r") as f:
            file_content = f.readlines()
        
        print(file_content)