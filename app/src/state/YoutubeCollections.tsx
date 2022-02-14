import { atom, atomFamily, selector, selectorFamily, waitForAll } from 'recoil';
import axios, { AxiosResponse } from 'axios';
import { userState } from './Auth';

const getYoutubeAccount = async () => {
	try {
		const response: AxiosResponse<YoutubeState> = await axios.get('/youtube/account');
		return response.data;
	} catch {
		return initialYoutubeAuthState;
	}
};

const initialYoutubeAuthState: YoutubeState = {
	email: '',
	refresh: false,
};

const authState = atom<YoutubeState>({
	key: 'youtubeAuthState',
	default: initialYoutubeAuthState,
});

export const authSelector = selector<YoutubeState>({
	key: 'youtubeAuth',
	get: async ({ get }) => {
		const youtubeAccount = get(authState);
		if (!youtubeAccount.email) {
			const user = get(userState);
			if (user) {
				return await getYoutubeAccount();
			}
			return initialYoutubeAuthState;
		}
		return youtubeAccount;
	},
	set: ({ set }, newValue) => set(authState, newValue),
});

const getYoutubeVideoCategories = async (opts: { channelId: YoutubeChannel['id'] | null }) => {
	try {
		const response: AxiosResponse<YoutubeVideoCategoriesResponse> = await axios.get(
			`/youtube/videos/categories${opts.channelId ? `?channel_id=${opts.channelId}` : ''}`
		);
		return response.data;
	} catch {
		return { categories: [] };
	}
};

const initialYoutubeVideoCategoriesState: YoutubeVideoCategoriesState = {
	channelId: null,
};

const videoCategoriesState = atomFamily<YoutubeVideoCategoriesState, YoutubeChannel['id'] | null>({
	key: 'youtubeVideoCategoriesState',
	default: (channelId) => ({ ...initialYoutubeVideoCategoriesState, channelId }),
});

export const videoCategoriesSelector = selectorFamily<YoutubeVideoCategoriesResponse, YoutubeChannel['id'] | null>({
	key: 'youtubeVideoCategories',
	get:
		(channelId) =>
		async ({ get }) => {
			const youtubeAccount = get(authSelector);
			if (!youtubeAccount.email) {
				return { categories: [] };
			}
			const { currentVideoCategoriesState } = get(
				waitForAll({ currentVideoCategoriesState: videoCategoriesState(channelId) })
			);
			return await getYoutubeVideoCategories(currentVideoCategoriesState);
		},
});

const getYoutubeVideos = async (options: YoutubeVideoOptions) => {
	const queryParams = [];
	options.selectedCategories.forEach((category) => {
		if (category !== -1) {
			queryParams.push(`video_categories=${category}`);
		}
	});
	if (options.channelId) {
		queryParams.push(`channel_id=${options.channelId}`);
	}
	try {
		const queryString = queryParams.length > 0 ? `?${queryParams.join('&')}` : '';
		const response: AxiosResponse<YoutubeVideosResponse> = await axios.get(
			`/youtube/videos/${options.page}/${options.perPage}${queryString}`
		);
		return response.data;
	} catch {
		return { videos: [], totalVideos: 0 };
	}
};

export const initialYoutubeVideosState: YoutubeVideosState = {
	page: 1,
	perPage: 50,
	selectedCategories: [],
	channelId: null,
};

export const videoOptionsState = atomFamily<YoutubeVideosState, YoutubeChannel['id'] | null>({
	key: 'youtubeVideosState',
	default: (channelId) => ({ ...initialYoutubeVideosState, channelId }),
});

export const videosSelector = selectorFamily<YoutubeVideosResponse, YoutubeChannel['id'] | null>({
	key: 'youtubeVideos',
	get:
		(channelId) =>
		async ({ get }) => {
			const youtubeAccount = get(authSelector);
			if (!youtubeAccount.email) {
				return { videos: [], totalVideos: 0 };
			}
			const { currentVideoOptionsState } = get(waitForAll({ currentVideoOptionsState: videoOptionsState(channelId) }));
			return await getYoutubeVideos(currentVideoOptionsState);
		},
});

const getYoutubeSubscriptions = async (options: PageState) => {
	try {
		const response: AxiosResponse<YoutubeSubscriptionsResponse> = await axios.get(
			`/youtube/subscriptions/${options.page}/${options.perPage}`
		);
		return response.data;
	} catch {
		return { subscriptions: [], totalSubscriptions: 0 };
	}
};

export const initialYoutubeSubscriptionsState: YoutubeSubscriptionsState = {
	page: 1,
	perPage: 50,
};

export const subscriptionOptionsState = atom<YoutubeSubscriptionsState>({
	key: 'youtubeSubscriptionsState',
	default: initialYoutubeSubscriptionsState,
});

export const subscriptionsSelector = selector<YoutubeSubscriptionsResponse>({
	key: 'youtubeSubscriptions',
	get: async ({ get }) => {
		const youtubeAccount = get(authSelector);
		if (!youtubeAccount.email) {
			return { subscriptions: [], totalSubscriptions: 0 };
		}
		const { currentSubscriptionOptionsState } = get(
			waitForAll({ currentSubscriptionOptionsState: subscriptionOptionsState })
		);
		return await getYoutubeSubscriptions(currentSubscriptionOptionsState);
	},
});
