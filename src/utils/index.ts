import fs from 'fs';
import path from 'path';

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

export function retryMethod(fn: () => void) {
    let i = 0;
    let attemps = RETRY_ATEMPS != undefined ? parseInt(RETRY_ATEMPS) : 5;

    while (i < attemps) {
        try {
            fn();
            return;
        } catch (error: any) {
            console.error(error);
        }
    }

    
}