import { atom, atomFamily } from 'recoil';

export const initialYoutubeAuthState: YoutubeState = {
	email: '',
	loaded: false,
};

export const initialYoutubeVideosView: YoutubeVideosViewState = {
	page: 1,
	per_page: 50,
	total_videos: 0,
	videos: [],
	categories: [],
	selectedCategories: [],
	channel_id: null,
	loaded: false,
};

export const initialYoutubeSubscriptionsView: YoutubeSubscriptionsViewState = {
	subscriptions: [],
	total_subscriptions: 0,
	page: 1,
	per_page: 50,
	loaded: false,
};

export const authAtom = atom<YoutubeState>({
	key: 'youtubeAuth',
	default: initialYoutubeAuthState,
});

export const videosAtom = atomFamily<YoutubeVideosViewState, YoutubeVideo['channel_id'] | null>({
	key: 'youtubeVideos',
	default: (channel_id) => ({ ...initialYoutubeVideosView, channel_id }),
});

export const subscriptionsAtom = atom<YoutubeSubscriptionsViewState>({
	key: 'youtubeSubscriptions',
	default: initialYoutubeSubscriptionsView,
});
