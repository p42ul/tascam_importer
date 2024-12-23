# Standard library
import argparse
import re
from pathlib import Path
import os

# Third-party
import ffmpeg
import librosa
from reathon.nodes import Project, Track, Item, Source


MASTER_PATTERN = re.compile(r'[0-9_]*TR1[56].wav')
TRACK_PATTERN = re.compile(r'TR[0-9][0-9]')


def main():
    parser = argparse.ArgumentParser(
        prog='TASCAM Model 16 Importer',
        description='Creates a REAPER project from a project file on an SD card from the TASCAM Model 16.',
    )
    parser.add_argument('source_dir')
    parser.add_argument('--mute-master', action='store_true',
                        help='If set, will mute the master channels (for example, channels 15 and 16 on a Model 16).')
    args = parser.parse_args()

    source_dir = Path(args.source_dir)
    if not source_dir.is_dir():
        print(f'{source_dir} is not a directory, exiting...')
        return

    wav_files = list(sorted([Path(f) for f in source_dir.rglob('*.wav')]))

    project_dir = Path('.', source_dir.name).resolve()
    print(f'creating project directory {project_dir}')
    project = Project()
    os.mkdir(project_dir.resolve())
    for wav in wav_files:
        length = librosa.get_duration(path=wav)
        if length == 0:
            print(f'skipping empty file {wav.name}')
            continue
        filename = os.path.splitext(wav.name)[0] + '.flac'
        outpath = os.path.abspath(project_dir.joinpath(filename))
        trackname = TRACK_PATTERN.findall(filename)[0]
        print(
            f'filename: {filename} outpath: {outpath} trackname: {trackname}')
        (ffmpeg
            .input(wav)
            .output(outpath)
            .run()
         )
        track = Track(name=trackname)
        track.add(
            Item(
                Source(file=outpath),
                position=0,
                length=length,
            )
        )
        if args.mute_master and MASTER_PATTERN.match(filename):
            print(f'muting {trackname}')
            track.props.append(['MUTESOLO', 1, 0, 0])
        project.add(track)

    project_file_path = project_dir.joinpath(f'{source_dir.name}.rpp')
    project.write(project_file_path)
    print(f'wrote to {project_file_path}')


if __name__ == '__main__':
    main()
