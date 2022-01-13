export {};

declare global {
	interface YoutubeState {
		email: string;
		refresh: boolean;
		loaded: boolean;
	}

	interface YoutubeVideo {
		id: string;
		title: string;
		thumbnail: string;
		channel_id: string;
		channel_title: string;
		published_at: string;
		category_id: number;
		created_at: string;
	}

	interface YoutubeSubscription {
		id: string;
		channel_id: string;
		channel_title: string;
		channel_thumbnail: string;
		email: string;
		published_at: string;
		created_at: string;
	}

	interface YoutubeVideoCategory {
		id: number;
		name: string;
		created_at: string;
	}

	interface PageState {
		page: number;
		per_page: 10 | 25 | 50;
	}

	interface FilterState {
		selectedCategories: number[];
	}

	interface Options extends Partial<FilterState>, Partial<PageState> {}

	interface YoutubeVideoResponse {
		total_videos: number;
		videos: YoutubeVideo[];
		categories: YoutubeVideoCategory[];
	}

	interface YoutubeVideosViewState extends YoutubeVideoResponse, FilterState, PageState {
		channel_id: string | null;
		loaded: bool;
	}

	interface YoutubeSubscriptionResponse {
		total_subscriptions: number;
		subscriptions: YoutubeSubscription[];
	}
	interface YoutubeSubscriptionsViewState extends PageState {
		subscriptions: YoutubeSubscription[];
		total_subscriptions: number;
		loaded: bool;
	}
}
