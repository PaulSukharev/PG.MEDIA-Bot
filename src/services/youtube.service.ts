import ytdl, { getInfo, videoInfo } from '@distube/ytdl-core';
import fs from 'fs';
import readline from 'readline';
import { Observable, concat, from, map, of, switchMap, zip } from 'rxjs'
import path from 'path';

import ffmpegPath from '@ffmpeg-installer/ffmpeg';
import ffmpeg from 'fluent-ffmpeg';
import { GoogleService } from './google.service';
import { google } from 'googleapis';
import { drawLivePicture } from './drawing.service';
import moment from 'moment';
import { Timestamp, Video } from '@models/video';
ffmpeg.setFfmpegPath(ffmpegPath.path)

const _tempDir = path.resolve(__dirname, '../../temp/');

export async function isYouTubeVideo(link: string | undefined) {
    if (link == undefined) {
        return false;
    }
    
    if (!ytdl.validateURL(link)) {
        return false;
    }

    const videoInfo = await ytdl.getBasicInfo(link);

    if (videoInfo.videoDetails.channelId != 'UCRMp-feWqFhOTpYpn8soqXQ') {
        return false;
    }

    return true;
}

export async function isLiveVideo(link: string | undefined) {
    if (link == undefined) {
        return false;
    }

    const videoInfo = await ytdl.getBasicInfo(link);
    return videoInfo.videoDetails.isLiveContent;
}

export async function getVideo(link: string) {
    const videoInfo = await ytdl.getInfo(link);
    return _mapVideo(videoInfo);
}

export async function createLivePicture(id: string): Promise<boolean> {
    try {
        const videoInfo = await ytdl.getInfo(id);
        const title = videoInfo.videoDetails.title.split('|')[0].trim();
        const date = moment(videoInfo.videoDetails.title.split('|')[1].trim(), "DD.MM.YYYY");
    
        const picture = await drawLivePicture(title, date);
        await uploadThumbnail(id, picture);
        fs.unlinkSync(picture);
        return true;
    } catch (error) {
        console.log(error);
        return false;
    }
}

export const getYoutubeVideoId = (link: string | undefined | null) => {
    if (!link) {
        return undefined;
    }
    const text = link.trim()
    let urlPattern = /https?:\/\/(?:www\.)?[\w\.-]+(?:\/[\w\.-]*)*(?:\?[\w\.\-]+=[\w\.\-]+(?:&[\w\.\-]+=[\w\.\-]+)*)?\/?/g
    let url = text.match(urlPattern)

    if (!(url && (url[0].includes('youtube') || url[0].includes('youtu.be')))) {
        return undefined;
    }

    const youtubeRegExp = /http(?:s?):\/\/(?:m\.|www\.)?(?:m\.)?youtu(?:be\.com\/(?:watch\?v=|embed\/|shorts\/)|\.be\/)([\w\-\_]*)(&(amp;)?[\w\?\=]*)?/;
    const match = text.match(youtubeRegExp);

    return match ? match[1] : undefined;
}

export const getTimestamps = async (id: string | undefined): Promise<Timestamp[]> => {
    if (!id) {
        return [];
    }
    const videoInfo = await getInfo(id);
    return _getVideoTimestamps(videoInfo);
};

export async function getPictureTypes(url: string | undefined) {
    if (url == undefined) {
        throw Error('URL is empty!');
    }

    const videoInfo = await getInfo(url);
    console.log(videoInfo);
}

export function downloadAndUploadVideo(url: string | undefined, timestamps: Timestamp[] | undefined): Observable<any> {
    if (url == undefined) {
        throw Error('URL is empty!');
    }

    if (timestamps == undefined || timestamps.length == 0) {
        throw Error('Timestamp was not selected!');
    }

    return from(ytdl.getInfo(url))
        .pipe(
            switchMap((videoInfo: ytdl.videoInfo) => {
                const id = videoInfo.videoDetails.videoId;

                const mergeVideoOutput = path.resolve(_tempDir, `${id}.mp4`);

                if (fs.existsSync(mergeVideoOutput)) {
                    return of(videoInfo);
                }

                const videoFormat = _getVideoFormat(videoInfo);
                const videoOutput = path.resolve(_tempDir, `${id}_video.mp4`);

                const audioFormat = _getAudioFormat(videoInfo);
                const audioOutput = path.resolve(_tempDir, `${id}_audio.mp4`);

                const video$ = from(_download(url, videoFormat, videoOutput));
                const audio$ = from(_download(url, audioFormat, audioOutput));

                return zip(video$, audio$)
                    .pipe(
                        switchMap(([video, audio]) => from(_mergeVideoAndAudio(video, audio, mergeVideoOutput))),
                        map(() => videoInfo)
                    )
            }),
            switchMap((videoInfo) => cut(videoInfo.videoDetails.videoId, timestamps)),
            switchMap((timestamp) => {
                if (timestamp == undefined) {
                    return of(false);
                }
                const file = `${_tempDir}/${timestamp.id}_${timestamp.start}.mp4`
                return uploadToYoutube(file, timestamp.title, timestamp.description);
            })
        );
}

function _mapVideo(videoInfo: videoInfo): Video {
    const video: Video = {
        id: videoInfo.videoDetails.videoId,
        title: videoInfo.videoDetails.title,
        description: videoInfo.videoDetails.description,
        date: moment(videoInfo.videoDetails.uploadDate),
        timestamps: _getVideoTimestamps(videoInfo)
    };
    return video;
}

function _download(url: string, format: ytdl.videoFormat, output: string): Promise<any> {
    return new Promise((resolve, reject) => {
        const video = ytdl(url, { format });

        let starttime: number;
        video.pipe(fs.createWriteStream(output));
        video.once('response', () => {
            starttime = Date.now();
        });
        video.on('progress', (chunkLength, downloaded, total) => {
            const percent = downloaded / total;
            const downloadedMinutes = (Date.now() - starttime) / 1000 / 60;
            const estimatedDownloadTime = (downloadedMinutes / percent) - downloadedMinutes;
            readline.cursorTo(process.stdout, 0);
            process.stdout.write(`${(percent * 100).toFixed(2)}% downloaded `);
            process.stdout.write(`(${(downloaded / 1024 / 1024).toFixed(2)}MB of ${(total / 1024 / 1024).toFixed(2)}MB)\n`);
            process.stdout.write(`running for: ${downloadedMinutes.toFixed(2)}minutes`);
            process.stdout.write(`, estimated time left: ${estimatedDownloadTime.toFixed(2)}minutes `);
            readline.moveCursor(process.stdout, 0, -1);
        });
        video.on('end', () => {
            process.stdout.write('\n\n');
            resolve(output);
        });
    });
}

export async function uploadToYoutube(file: string, title: string, description?: string) {
    const auth = GoogleService.getOauth2();

    const youtube = google.youtube({
        version: 'v3',
        auth: auth
    });

    return youtube.videos.insert({
        part: ['snippet', 'status'],
        requestBody: {
            snippet: {
                title: title,
                description: description
            },
            status: {
                privacyStatus: "private",
                madeForKids: false,
                selfDeclaredMadeForKids: false
            }
        },
        media: {
            body: fs.createReadStream(file),
        }
    })
}

async function uploadThumbnail(id: string, file: string) {
    const auth = GoogleService.getOauth2();

    const youtube = google.youtube({
        version: 'v3',
        auth: auth
    });

    return youtube.thumbnails.set({
        videoId: id,
        media: {
            mimeType: "image/jpeg",
            body: fs.createReadStream(file),
        }
    })
}

function _mergeVideoAndAudio(video: any, audio: any, output: string) {
    return new Promise((resolve, reject) => {
        const command = ffmpeg();

        command.input(video);
        command.input(audio);

        command.outputOptions('-c:v', 'copy')
        command.save(output);

        command.on('end', () => {
            resolve(true);
        });

        command.on('error', () => {
            resolve(false);
        })

        command.run();
    });
}

function cut(id: string, timestamps: Timestamp[]) {
    if (timestamps.length == 0) {
        throw new Error("Timestamps is empty");
    }

    const timestamps$ = timestamps.map(x => from(_cutTimestamp(id, x)));

    return concat(...timestamps$);
}

function _cutTimestamp(id: string, timestamp: Timestamp): Promise<Timestamp | undefined> {
    return new Promise((resolve, reject) => {
        const video = `${_tempDir}/${id}.mp4`;
        const out = `${_tempDir}/${id}_${timestamp.start}.mp4`;

        if (fs.existsSync(out)) {
            resolve(timestamp);
            return;
        }

        const command = ffmpeg();

        command.input(video);
        command.setStartTime(timestamp.start);
        command.setDuration(timestamp.end - timestamp.start);

        command.outputOptions('-c:v', 'copy')
        command.output(out);

        command.on('end', () => {
            resolve(timestamp);
        });

        command.on('error', () => {
            resolve(undefined);
        })

        command.run();
    });
}

function _getVideoFormat(videoInfo: ytdl.videoInfo) {
    const formats = videoInfo.formats.filter(x => x.qualityLabel?.includes('1080'));

    if (formats == undefined || formats.length == 0) {
        throw new Error("Not found 1080p quality");
    }

    return formats[0];
}

function _getAudioFormat(videoInfo: ytdl.videoInfo) {
    const format = ytdl.chooseFormat(videoInfo.formats, { filter: 'audioonly' });

    if (format == undefined) {
        throw new Error("Not found audio");
    }

    return format;
}

function _getVideoTimestamps(videoInfo: videoInfo): Timestamp[] {
    try {
        const videoLength = videoInfo.videoDetails.lengthSeconds;
        const description = videoInfo.videoDetails.description;
    
        const timestamps: Timestamp[] = [];
    
        if (description == null || description == "") {
            return timestamps;
        }
    
        for (let str of description.split('\n')) {
            const result = str.match(/^(?:(?:([01]?\d|2[0-3]):)?([0-5]?\d):)?([0-5]?\d)/g);
    
            if (result == null) {
                continue;
            }
    
            const time = result[0];
            const duration = _timeToSeconds(time);
            const title = str.slice(str.indexOf(" ")).trim();
    
            if (timestamps.length > 0) {
                const prev = timestamps[timestamps.length - 1];
                prev.end = duration;
            }

            moment.locale('ru');
    
            const timestamp: Timestamp = {
                id: videoInfo.videoDetails.videoId,
                start: duration,
                end: 0,
                title: title,
                description: moment(videoInfo.videoDetails.uploadDate).format('D MMMM YYYY')
            }
    
            timestamps.push(timestamp);
        }
    
        const last = timestamps[timestamps.length - 1];
        last.end = Number(videoLength);

        return timestamps;
    } catch (error) {
        return [];
    }
}

function _timeToSeconds(time: string): number {
    const times = time.split(':').reverse();

    if (times.length == 3) {
        let [s = 0, m = 0, h = 0] = times;
        return (+h) * 3600 + (+m) * 60 + (+s);
    }

    if (times.length == 2) {
        let [s = 0, m = 0] = times;
        return (+m) * 60 + (+s);
    }

    return 0;
}

module.exports = {
    isYouTubeVideo,
    getVideo,
    getPictureTypes,
    getYoutubeVideoId,
    getTimestamps,
    downloadAndUploadVideo,
    uploadToYoutube,
    createLivePicture
}