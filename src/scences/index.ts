import { Stage } from "telegraf/scenes";
import startScene from "./start";
import youtube from "./youtube/youtube";
import youtubePicture from "./youtube/youtube.picture";
import youtubePictureSermon from "./youtube/youtube.picture.sermon";
import youtubePictureLive from "./youtube/youtube.picture.live";
import youtubeAudio from "./youtube/youtube.audio";

const stage = new Stage([
    startScene,
    youtube,
    youtubePicture,
    youtubePictureSermon,
    youtubePictureLive,
    youtubeAudio
  ]);

export default stage;