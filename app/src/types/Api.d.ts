export {};

declare global {
	interface ValidationError {
		loc: string[];
		msg: string;
		type: string;
	}

	interface ErrorResponse {
		detail: ValidationError[] | string;
	}

	interface CreateFileJobBody {
		file: File;
		artworkUrl: string;
		title: string;
		artist: string;
		album: string;
		grouping?: string;
	}

	interface CreateYoutubeJobBody {
		youtubeUrl: string;
		artworkUrl: string;
		title: string;
		artist: string;
		album: string;
		grouping?: string;
	}

	interface JobsResponse {
		jobs: Job[];
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

	interface DownloadResponse {
		url: string;
	}

	interface YoutubeAuthState {
		email: string;
		refresh: boolean;
	}

	interface YoutubeVideoCategoriesResponse {
		categories: YoutubeVideoCategory[];
	}

	interface ChannelBody {
		channelID?: string;
	}

	interface PageBody {
		perPage: number;
		page: number;
	}

	interface YoutubeVideosBody extends ChannelBody, PageBody {
		selectedCategories?: number[];
		likedOnly?: boolean;
		queuedOnly?: boolean;
	}

	interface YoutubeVideosResponse {
		videos: YoutubeVideo[];
	}

	interface YoutubeVideoBody {
		videoID: string;
		relatedLength?: number;
	}

	interface YoutubeVideoResponse {
		video: YoutubeVideo;
		relatedVideos: YoutubeVideo[];
	}

	type YoutubeSubscriptionBody = ChannelBody & PageBody;

	interface YoutubeSubscriptionsResponse {
		subscriptions: YoutubeSubscription[];
	}

	interface YoutubeVideoQueueResponse {
		prev: boolean;
		next: boolean;
		currentVideo: YoutubeVideo;
	}
}
