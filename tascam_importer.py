import argparse
import re
import librosa

from pathlib import Path
from reathon.nodes import Project, Track, Item, Source

# Mute the master channel
MUTE_PATTERN = re.compile(r'[0-9_]*TR1[56].wav')


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
        track = Track()
        track.add(
            Item(
                source,
                position=0,
                length=length
            )
        )
        if args.mute_master and MUTE_PATTERN.match(source.file.name):
            print(f'muting {source.file}')
            track.mute()
        project.add(track)

    project.write(project_name)
    print(f'wrote to {project_name}')


if __name__ == '__main__':
    main()
