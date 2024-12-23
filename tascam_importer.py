import argparse
import re
import librosa

from pathlib import Path
from reathon.nodes import Project, Track, Item, Source

MASTER_PATTERN = re.compile(r'[0-9_]*TR1[56].wav')
TRACK_PATTERN = re.compile(r'TR[0-9][0-9]')


def main():
    parser = argparse.ArgumentParser(
        prog='TASCAM Model 16 Importer',
        description='Creates a REAPER project from a project file on an SD card from the TASCAM Model 16.',
    )
    parser.add_argument('project_dir')
    parser.add_argument('--mute-master', action='store_true',
                        help='If set, will mute the master channels (for example, channels 15 and 16 on a Model 16).')
    args = parser.parse_args()

    project_dir = Path(args.project_dir)
    if not project_dir.is_dir():
        print(f'{project_dir} is not a directory, exiting...')
        return

    project_name = f'{project_dir.name}.rpp'
    project = Project()
    sources = [
        Source(file=wav_file.resolve())
        for wav_file in sorted(project_dir.rglob("*.wav"))
    ]

    for source in sources:
        length = librosa.get_duration(path=source.file)
        if length == 0:
            print(f'skipping empty file {source.file}')
            continue
        track = Track(name=TRACK_PATTERN.findall(source.file.name)[0])
        track.add(
            Item(
                source,
                position=0,
                length=length,
            )
        )
        if args.mute_master and MASTER_PATTERN.match(source.file.name):
            print(f'muting {source.file}')
            track.mute()
        project.add(track)

    project.write(project_name)
    print(f'wrote to {project_name}')


if __name__ == '__main__':
    main()
