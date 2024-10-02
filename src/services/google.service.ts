import { google } from "googleapis";

export class GoogleService {

    scopes = [
        'https://www.googleapis.com/auth/youtube.force-ssl',
        'https://www.googleapis.com/auth/userinfo.profile',
        'https://www.googleapis.com/auth/youtube.upload'
    ]

    public static async getUserInfo(token: string) {

        const oauth2Client = new google.auth.OAuth2();
        oauth2Client.setCredentials({ access_token: token });

        const oauth2 = google.oauth2({
            auth: oauth2Client,
            version: 'v2'
        });

        let { data } = await oauth2.userinfo.get();

        return data;
    }

    public static getOauth2() {

        const oauth2Client = new google.auth.OAuth2(
            process.env.CLIENT_ID,
            process.env.CLIENT_SECRET
        );

        oauth2Client.setCredentials({
            refresh_token: process.env.REFRESH_TOKEN
        });

        return oauth2Client;
    }
}
