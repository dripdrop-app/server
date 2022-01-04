import axios, { AxiosResponse } from 'axios';
import { atom, atomFamily } from 'recoil';

export const initialYoutubeAuthState: YoutubeState = {
	email: '',
};

export const initialYoutubeVideosView: YoutubeVideosViewState = {
	page: 1,
	per_page: 50,
	total_videos: 0,
	videos: [],
	categories: [],
	selectedCategories: [],
	channel_id: null,
};

export const initialYoutubeSubscriptionsView: YoutubeSubscriptionsViewState = {
	subscriptions: [],
	total_subscriptions: 0,
	page: 1,
	per_page: 50,
};

export const authAtom = atom<YoutubeState>({
	key: 'youtubeAuth',
	default: (async () => {
		try {
			const response: AxiosResponse<YoutubeState> = await axios.get('/youtube/account');
			return response.data;
		} catch {}
		return initialYoutubeAuthState;
	})(),
});

export const videosAtom = atomFamily<YoutubeVideosViewState, YoutubeVideo['channel_id'] | null>({
	key: 'youtubeVideosAtom',
	default: async (channel_id) =>
		(async () => {
			try {
				const response: AxiosResponse<YoutubeVideoResponse> = await axios.get(
					`/youtube/videos/${initialYoutubeVideosView.page}/${initialYoutubeVideosView.per_page}`,
					{ params: channel_id ? { channel_id } : {} }
				);
				return { ...initialYoutubeVideosView, channel_id, ...response.data };
			} catch {}
			return initialYoutubeVideosView;
		})(),
});

export const subscriptionsAtom = atom<YoutubeSubscriptionsViewState>({
	key: 'youtubeSubscriptionsAtom',
	default: (async () => {
		try {
			const response: AxiosResponse<YoutubeSubscriptionResponse> = await axios.get(
				`/youtube/subscriptions/${initialYoutubeSubscriptionsView.page}/${initialYoutubeSubscriptionsView.per_page}`
			);
			return { ...initialYoutubeSubscriptionsView, ...response.data };
		} catch {}
		return initialYoutubeSubscriptionsView;
	})(),
});
