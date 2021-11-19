import { FILE_TYPE } from '../utils/enums';

declare global {
	interface MusicForm {
		fileType: keyof typeof FILE_TYPE;
		youtube_url: string;
		filename: string;
		artwork_url: string;
		title: string;
		artist: string;
		album: string;
		grouping: string;
	}

	interface Job
		extends Pick<MusicForm, 'youtube_url' | 'filename' | 'artwork_url' | 'title' | 'artist' | 'album' | 'grouping'> {
		job_id: string;
		completed: boolean;
		failed: boolean;
	}
}
