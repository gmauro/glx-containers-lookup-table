import os

from bioblend.galaxy import GalaxyInstance
from comoda import path_exists
from comoda.yaml import dump
from galaxy.tools.deps.conda_util import requirements_to_conda_targets
from galaxy.tools.deps.mulled.util import (
    build_target,
    image_name,
    mulled_tags_for,
    split_tag,
)
from galaxy.tools.deps.requirements import parse_requirements_from_xml
from galaxy.util.xml_macros import load
from src import *


help_doc = """
Build lookup table 
"""


def make_parser(parser):
    parser.add_argument('-p', '--sg-local-path', type=str, metavar='PATH',
                        dest='sg_local_path',
                        help='Singularity images local path',
                        default="/cvmfs/singularity.galaxyproject.org/all")
    parser.add_argument('-u', '--url', type=str,
                        help='Galaxy server url',
                        required=True)
    parser.add_argument('-k', '--key', type=str,
                        help='Galaxy user api key',
                        required=True)
    parser.add_argument('-m', '--matched', type=str,
                        help='File with the list of tool id with a container match',
                        default='matched.yaml')
    parser.add_argument('-n', '--notmatched', type=str,
                        help='File with the list of tool id without a container match',
                        default='unmatched.yaml')


def mulled_container_name(namespace, targets):
    name = None

    if len(targets) == 1:
        target = targets[0]
        target_version = target.version
        tags = mulled_tags_for(namespace, target.package_name)

        if not tags:
            return None

        if target_version:
            for tag in tags:
                version, build = split_tag(tag)
                if version == target_version:
                    name = "%s:%s--%s" % (target.package_name, version, build)
                    break
        else:
            version, build = split_tag(tags[0])
            name = "%s:%s--%s" % (target.package_name, version, build)
    else:
        base_image_name = image_name(targets)
        tags = mulled_tags_for(namespace, base_image_name)
        if tags:
            name = "%s:%s" % (base_image_name, tags[0])

    if name:
        return "quay.io/%s/%s" % (namespace, name)


def implementation(logger, args):
    list_of_files = {}
    if path_exists(args.sg_local_path, logger=logger, force=True):
        for (dirpath, dirnames, filenames) in os.walk(args.sg_local_path):
            for filename in filenames:
                list_of_files[filename] = os.sep.join([dirpath, filename])
        logger.debug(list_of_files)

    gi = GalaxyInstance(args.url, key=args.key)
    tools = gi.tools.get_tools()

    counter_singularity = 0
    counter_docker = 0
    match = {}
    unmatch = []

    for t in tools:
        t_id = t['id']
        t_xml_file = gi.tools.show_tool(t['id'])['config_file']

        container_name = None
        try:
            tool_xml = load(t_xml_file)
            requirements, containers = parse_requirements_from_xml(tool_xml)
            conda_targets = requirements_to_conda_targets(requirements)
            mulled_targets = [build_target(c.package, c.version) for c in conda_targets]
            container_name = mulled_container_name("biocontainers", mulled_targets)
        except Exception as ex:
            logger.exception('Caught an error at {} with tid: {}'.format(args.url, t_id))
            pass

        singularity = 'not_found'
        if container_name:
            counter_docker += 1
            if os.path.basename(container_name) in list_of_files:
                singularity = os.path.join(args.sg_local_path, os.path.basename(container_name))
                counter_singularity += 1

            match[t_id] = {'docker': container_name.replace('quay.io', 'quay.io:/'),
                           'singularity': singularity}
        unmatch.append(t_id)
        print(t_id, container_name, singularity)
    dump(match, "{}_{}".format(args.url.split('/')[2], args.matched))
    dump(unmatch, "{}_{}".format(args.url.split('/')[2], args.notmatched))

    print("number of tools {}".format(len(tools)))
    print("number of docker images matched {}".format(counter_docker))
    print("number of singularity images in CVMFS {}".format(len(list_of_files)))
    print("number of singularity images matched {}".format(counter_singularity))


def do_register(registration_list):
    registration_list.append(('build', help_doc, make_parser, implementation))
