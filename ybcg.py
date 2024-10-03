import yaml
import os
import subprocess

def load_yaml(yaml_file):
    with open(yaml_file, 'r') as file:
        return yaml.safe_load(file)

def create_directory_structure():
    os.makedirs('include', exist_ok=True)
    os.makedirs('src', exist_ok=True)

def create_cpp_files(cpp_names):
    for name in cpp_names:
        with open(f'include/{name}.hpp', 'w') as header_file:
            header_file.write(f'#pragma once\n\n')

        with open(f'src/{name}.cpp', 'w') as source_file:
            source_file.write(f'#include "../include/{name}.hpp"\n\n')

def create_cuda_files(cuda_names):
    for name in cuda_names:
        with open(f'include/{name}.cuh', 'w') as header_file:
            header_file.write(f'#pragma once\n\n')

        with open(f'src/{name}.cu', 'w') as source_file:
            source_file.write(f'#include "../include/{name}.cuh"\n\n')

def create_utils_header(languages):
    with open('include/utils.hpp', 'w') as utils_file:
        utils_file.write(
            '#pragma once\n'
            '#include <bits/extc++.h>\n'
        )
        if 'cuda' in languages:
            utils_file.write(
            '#include <cuda_runtime.h>\n'
            '#include <device_launch_parameters.h>\n'
        )

def create_main_cpp():
    with open('src/main.cpp', 'w') as main_file:
        main_file.write(
            '#include <iostream>\n'
            '#include "../include/utils.hpp"\n'
            'using namespace std;\n\n'
            'int main(int argc, char** argv) {\n'
            '    cout << "Hello, World!" << endl;\n'
            '    return 0;\n'
            '}\n'
        )

def create_cmakelists(yaml_data):
    project_name = yaml_data.get('project_name', 'MyProject')
    cpp_version = yaml_data.get('cpp_standard', 17)
    languages = yaml_data.get('languages', [])
    libraries = yaml_data.get('libraries', [])
    links = yaml_data.get('link', [])
    compile_options = yaml_data.get('compile_options', [])

    with open('CMakeLists.txt', 'w') as cmake_file:
        cmake_file.write(f'cmake_minimum_required(VERSION 3.10)\n')
        cmake_file.write(f'project({project_name})\n\n')

        cmake_file.write('set(CMAKE_CXX_STANDARD {})\n\n'.format(cpp_version))
        cmake_file.write('add_executable(main src/main.cpp)\n\n')
        cmake_file.write('include_directories(include)\n\n')
        cmake_file.write('target_precompile_headers(main PRIVATE include/utils.hpp)\n\n')
        if 'cuda' in languages:
            cmake_file.write('enable_language(CUDA)\n')

        for lib in libraries:
            cmake_file.write(f'find_package({lib} REQUIRED)\n')
        if 'cuda' in languages:
            cmake_file.write(f'find_package(CUDAToolkit REQUIRED)\n')

        if compile_options:
            cmake_file.write(f'target_compile_options(main PRIVATE {" ".join(compile_options)})\n\n')

        cmake_file.write('target_include_directories(main PRIVATE include)\n')
        cmake_file.write('target_link_libraries(main PRIVATE')
        if 'cuda' in languages:
            cmake_file.write(' CUDA::cudart')
        for link in links:
            cmake_file.write(f' {link}')
        cmake_file.write(')\n')

def precompile_utils():
    subprocess.run(['mkdir', 'build'])
    os.chdir('build')
    subprocess.run(['cmake', '..'])
    subprocess.run(['make'])
    os.chdir('..')

def generate_project(yaml_file):
    yaml_data = load_yaml(yaml_file)

    create_directory_structure()

    create_cpp_files(yaml_data.get('cpp', []))
    create_cuda_files(yaml_data.get('cuda', []))

    create_utils_header(yaml_data.get('languages', []))
    create_main_cpp()

    create_cmakelists(yaml_data)

    precompile_utils()

if __name__ == "__main__":
    yaml_file_path = 'project_config.yaml'
    generate_project(yaml_file_path)