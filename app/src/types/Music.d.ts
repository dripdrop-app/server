import { FILE_TYPE } from '../utils/enums';

declare global {
	interface Job {
		id: string;
		youtubeUrl?: string;
		filename?: string;
		artworkUrl?: string;
		title: string;
		artist: string;
		album: string;
		grouping?: string;
		completed: boolean;
		failed: boolean;
		createdAt: string;
	}

	interface MusicFormState {
		fileType: keyof typeof FILE_TYPE;
		youtubeUrl: string;
		filename: string;
		artworkUrl: string;
		title: string;
		artist: string;
		album: string;
		grouping: string;
	}

	type JobsState = JobsResponse;

	type PageState = PageBody;
}
