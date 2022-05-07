export {};

declare global {
	interface YoutubeVideo {
		id: string;
		title: string;
		thumbnail: string;
		channelId: string;
		channelTitle: string;
		publishedAt: string;
		categoryId: number;
		createdAt: string;
		liked: string | null;
		queued: string | null;
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

	interface VideoMap {
		[page: number]: YoutubeVideo[];
	}
}
