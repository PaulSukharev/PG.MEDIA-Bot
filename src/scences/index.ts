import { Stage } from "telegraf/scenes";
import startScene from "./start";
import youtube from "./youtube/youtube";
import youtubePicture from "./youtube/youtube.picture";

const stage = new Stage([
    startScene,
    youtube,
    youtubePicture
  ]);

export default stage;