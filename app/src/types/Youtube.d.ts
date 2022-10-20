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
	watched: string | null;
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
	channelId?: string;
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
