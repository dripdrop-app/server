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
		perPage: number;
	}

	interface FilterState {
		selectedCategories: number[];
	}

	interface ChannelState {
		channelId?: string;
	}

	type YoutubeVideoOptions = PageState & FilterState & ChannelState;

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

	type YoutubeVideoCategoriesState = YoutubeVideoCategoriesResponse & ChannelState;

	type YoutubeVideosState = FilterState & PageState & YoutubeVideosResponse & ChannelState;

	type YoutubeSubscriptionsState = PageState & YoutubeSubscriptionsResponse;
}
