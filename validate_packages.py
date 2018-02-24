#!/usr/bin/python
import sys
import os
import re
import hashlib
import json

def parse_setup_ini(setup_ini_path):
    packages = {}
    setup_ini = open(setup_ini_path, "r")
    package_field_re = re.compile(r"^(.+?): (.+)$")
    package_section_re = re.compile(r"^\[(.+)\]$")
    
    current_package_name = None
    skip_section = False
    for line in setup_ini:
        if line.startswith("@ "):
            current_package_name = line[2:].strip()
            packages[current_package_name] = {}
            skip_section = False
        else:
            if current_package_name != None:
                section_match = package_section_re.match(line)
                if section_match:
                    skip_section = True if section_match.group(1) != 'curr' else False

                if not skip_section:
                    matches = package_field_re.match(line)
                    if matches:
                        key = matches.group(1)
                        value = matches.group(2)
                        if key == 'install' or key == 'source':
                            (file_path, file_size, sha512) = value.split(' ')
                            packages[current_package_name][key] = { "path": file_path, "size": long(file_size), "sha512": sha512 }
                        elif key == 'requires':
                            packages[current_package_name][key] = value.split(' ')
                        else:
                            packages[current_package_name][key] = value

    return packages

def validate_arch_dir(package_list, archdir):
    errors = {}
    counter = 0
    for package in package_list.iterkeys():
        packageErrors = {}
        package_install_details = package_list[package]["install"]
        file_path = package_install_details["path"]
        file_size = package_install_details["size"]
        file_sha512 = package_install_details["sha512"]
        
        full_file_path = os.path.join(archdir, file_path)
        if not os.path.isfile(full_file_path):
            packageErrors["file_not_exists"] = False
        else:
            actual_size = os.path.getsize(full_file_path)
            if actual_size != file_size:
                packageErrors["wrong_size"] = "{0}, expected {1}".format(actual_size, file_size)

            hasher = hashlib.new('sha512')
            with open(full_file_path, 'rb') as f:
                hasher.update(f.read())
            actual_sha512 = hasher.hexdigest()
            if file_sha512 != actual_sha512:
                packageErrors["wrong_sha512"] = actual_sha512

        if packageErrors:
            errors[package] = packageErrors

        counter += 1
        if counter % 500 == 0:
            print "Processed {0} packages".format(counter)

    return errors


def main():
    distdir = sys.argv[1]
    print "distdir = %s" % distdir

    for archdir in (d for d in os.listdir(distdir)
                    if os.path.isdir(os.path.join(distdir, d)) and os.path.isfile(os.path.join(distdir, d, "setup.ini"))):
        print "Scanning architecture: %s" % archdir
        print "====================="
        print "Parsing setup.ini..."
        packages = parse_setup_ini(os.path.join(distdir, archdir, "setup.ini"))
        print "Validating {0} packages...".format(len(packages))
        errors = validate_arch_dir(packages, distdir)
        print "Found {0} package errors".format(len(errors))

        errors_filename = os.path.join(distdir, "{0}_errors.json".format(archdir))
        with open(errors_filename, "w") as errors_file:
            json.dump(errors, errors_file, indent=4, separators=(',', ': '))
        print "Errors written to: {0}".format(errors_filename)
        print "====================="

if __name__ == "__main__":
    main()
