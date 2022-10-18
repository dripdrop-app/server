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

type MusicFormState =
	| {
			fileSwitch: true;
			youtubeUrl: string;
			file: File;
			artworkUrl: string;
			title: string;
			artist: string;
			album: string;
			grouping: string;
	  }
	| {
			fileSwitch: false;
			youtubeUrl: string;
			file: null;
			artworkUrl: string;
			title: string;
			artist: string;
			album: string;
			grouping: string;
	  };

type JobsState = JobsResponse;

type PageState = PageBody;

interface JobsResponse {
	jobs: Job[];
	totalPages: number;
}

interface GroupingResponse {
	grouping: string;
}

interface Artwork {
	artworkUrl: string;
}

interface TagsResponse {
	artworkUrl?: string;
	title?: string;
	artist?: string;
	album?: string;
	grouping?: string;
}
