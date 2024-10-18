import fs from 'fs';
import path from 'path';

export function removeAllFilesSync(directory: string) {
    const files = fs.readdirSync(directory);
    
    for (const file of files) {
        const filePath = path.join(directory, file);
        fs.unlinkSync(filePath);
    }
}