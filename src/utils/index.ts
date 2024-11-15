import fs from 'fs';
import path from 'path';

import * as dotenv from 'dotenv'

dotenv.config()

const { RETRY_ATEMPS } = process.env;

export function removeAllFilesSync(directory: string) {
    if (!fs.existsSync(directory)) {
        fs.mkdirSync(directory);
        return;
    }
    const files = fs.readdirSync(directory);
    
    for (const file of files) {
        const filePath = path.join(directory, file);
        fs.unlinkSync(filePath);
    }
}

export function retryMethod(fn: any, args: any) {
    let i = 0;
    let attemps = RETRY_ATEMPS != undefined ? parseInt(RETRY_ATEMPS) : 5;

    while (i < attemps) {
        try {
            const res = fn(args);
            return res;
        } catch (error: any) {
            console.error(error);
        }
    }
}

export async function retryPromiseMethod(fn: any) {
    let i = 0;
    let attemps = RETRY_ATEMPS != undefined ? parseInt(RETRY_ATEMPS) : 5;

    while (i < attemps) {
        try {
            const res = await fn();
            return res;
        } catch (error: any) {
            console.error(error);
        }
    }
}
