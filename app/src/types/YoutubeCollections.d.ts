export {};

declare global {
	interface YoutubeState {
		email: string;
		refresh: boolean;
	}

	interface YoutubeVideo {
		id: string;
		title: string;
		thumbnail: string;
		channelId: string;
		channelTitle: string;
		publishedAt: string;
		categoryId: number;
		createdAt: string;
	}

	interface YoutubeChannel {
		id: string;
		title: string;
		thumbnail?: string;
		uploadPlaylistId?: string;
		createdAt: string;
		lastUpdated: string;
	}

	interface YoutubeSubscription {
		id: string;
		channelId: string;
		channelTitle: string;
		channelThumbnail: string;
		email: string;
		publishedAt: string;
		createdAt: string;
	}

	interface YoutubeVideoCategory {
		id: number;
		name: string;
		createdAt: string;
	}

	interface PageState {
		page: number;
		perPage: 10 | 25 | 50;
	}

	interface FilterState {
		selectedCategories: number[];
	}

	interface YoutubeVideoOptions extends PageState, FilterState {
		channelId: string | null;
	}

	interface YoutubeVideoCategoriesResponse {
		categories: YoutubeVideoCategory[];
	}

	interface YoutubeVideosResponse {
		totalVideos: number;
		videos: YoutubeVideo[];
	}

	interface YoutubeSubscriptionsResponse {
		totalSubscriptions: number;
		subscriptions: YoutubeSubscription[];
	}

	interface YoutubeVideoCategoriesState {
		channelId: string | null;
	}

	interface YoutubeVideosState extends FilterState, PageState {
		channelId: string | null;
	}

	interface YoutubeSubscriptionsState extends PageState {}
}
