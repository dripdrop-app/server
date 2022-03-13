import { atom } from 'jotai';
import axios, { AxiosResponse } from 'axios';
import { userAtomState } from './Auth';
import { atomFamily } from 'jotai/utils';
import _ from 'lodash';

const initialYoutubeauthAtomState: YoutubeState = {
	email: '',
	refresh: false,
};

const authAtom = atom({ loading: true, data: initialYoutubeauthAtomState });

export const authAtomState = atom(
	(get) => get(authAtom),
	(get, set, update: YoutubeState | undefined) => {
		const userState = get(userAtomState);
		if (update) {
			return set(authAtom, { loading: false, data: update });
		}
		const getYoutubeAccount = async () => {
			set(authAtom, { loading: true, data: initialYoutubeauthAtomState });
			try {
				const response: AxiosResponse<YoutubeState> = await axios.get('/youtube/account');
				set(authAtom, { loading: false, data: response.data });
			} catch {
				set(authAtom, { loading: false, data: initialYoutubeauthAtomState });
			}
		};
		if (userState.data.authenticated) {
			getYoutubeAccount();
		}
	}
);

authAtomState.onMount = (setAtom) => setAtom();

const initialYoutubeVideoCategoriesState: YoutubeVideoCategoriesState = {
	channelId: undefined,
	categories: [],
};

const youtubeVideoCategoriesAtom = atomFamily((channelId: YoutubeVideoCategoriesState['channelId']) =>
	atom({ loading: true, data: { ...initialYoutubeVideoCategoriesState, channelId } })
);

export const youtubeVideoCategoriesAtomState = atomFamily((channelId: YoutubeVideoCategoriesState['channelId']) => {
	const subAtom = atom(
		(get) => get(youtubeVideoCategoriesAtom(channelId)),
		(get, set, update) => {
			const youtubeAuth = get(authAtomState);
			const currentState = get(youtubeVideoCategoriesAtom(channelId));
			const getYoutubeVideoCategories = async (channelId: YoutubeVideoCategoriesState['channelId']) => {
				set(youtubeVideoCategoriesAtom(channelId), { loading: true, data: { channelId, categories: [] } });
				try {
					const response: AxiosResponse<YoutubeVideoCategoriesResponse> = await axios.get(
						`/youtube/videos/categories${channelId ? `?channel_id=${channelId}` : ''}`
					);
					set(youtubeVideoCategoriesAtom(channelId), {
						loading: false,
						data: { channelId, categories: response.data.categories },
					});
				} catch {
					set(youtubeVideoCategoriesAtom(channelId), {
						loading: false,
						data: { channelId, categories: [] },
					});
				}
			};
			if (youtubeAuth.data.email && !currentState.data.categories.length) {
				getYoutubeVideoCategories(channelId);
			}
		}
	);
	subAtom.onMount = (setAtom) => setAtom();
	return subAtom;
});

export const initialYoutubeVideosState: YoutubeVideosState = {
	page: 1,
	perPage: 50,
	selectedCategories: [],
	channelId: undefined,
	videos: [],
	totalVideos: 0,
};

const youtubeVideosAtom = atomFamily((channelId: YoutubeVideosState['channelId']) =>
	atom({ loading: true, data: { ...initialYoutubeVideosState, channelId } })
);

export const youtubeVideosAtomState = atomFamily((channelId: YoutubeVideosState['channelId']) => {
	const subAtom = atom(
		(get) => get(youtubeVideosAtom(channelId)),
		(get, set, update: YoutubeVideoOptions | undefined) => {
			const youtubeAuth = get(authAtomState);
			const currentState = get(youtubeVideosAtom(channelId));
			if (update) {
				currentState.data = { ...currentState.data, ...update };
			} else {
				const keys = ['perPage', 'page', 'selectedCategories', 'channelId'];
				const origOptions = _.pick({ ...initialYoutubeVideosState, channelId }, keys);
				const currOptions = _.pick(currentState.data, keys);
				if (_.isEqual(origOptions, currOptions) && currentState.data.videos.length) {
					return;
				}
				currentState.data = { ...initialYoutubeVideosState, channelId };
			}
			const getYoutubeVideos = async () => {
				const queryParams = [];
				const options = currentState.data;
				options.selectedCategories.forEach((category) => {
					queryParams.push(`video_categories=${category}`);
				});
				if (options.channelId) {
					queryParams.push(`channel_id=${options.channelId}`);
				}
				set(youtubeVideosAtom(channelId), (prev) => ({ data: { ...prev.data, ...options }, loading: true }));
				try {
					const queryString = queryParams.length > 0 ? `?${queryParams.join('&')}` : '';
					const response: AxiosResponse<YoutubeVideosResponse> = await axios.get(
						`/youtube/videos/${options.page}/${options.perPage}${queryString}`
					);
					set(youtubeVideosAtom(channelId), (prev) => ({
						data: { ...prev.data, ...response.data },
						loading: false,
					}));
				} catch {
					set(youtubeVideosAtom(channelId), (prev) => ({
						data: { ...prev.data, videos: [], totalVideos: 0 },
						loading: false,
					}));
				}
			};
			if (youtubeAuth.data.email) {
				getYoutubeVideos();
			}
		}
	);
	subAtom.onMount = (setAtom) => setAtom();
	return subAtom;
});

export const initialYoutubeSubscriptionsState: YoutubeSubscriptionsState = {
	page: 1,
	perPage: 50,
	totalSubscriptions: 0,
	subscriptions: [],
};

const youtubeSubscriptionsAtom = atom({ loading: true, data: initialYoutubeSubscriptionsState });

export const youtubeSubscriptionsAtomState = atom(
	(get) => get(youtubeSubscriptionsAtom),
	(get, set, update: PageState | undefined) => {
		const youtubeAuth = get(authAtomState);
		const currentState = get(youtubeSubscriptionsAtom);
		if (update) {
			currentState.data = { ...currentState.data, ...update };
		} else {
			const keys = ['perPage', 'page'];
			const origOptions = _.pick(initialYoutubeSubscriptionsState, keys);
			const currOptions = _.pick(currentState.data, keys);
			console.log(origOptions, currOptions);
			if (_.isEqual(origOptions, currOptions) && currentState.data.subscriptions.length) {
				return;
			}
			currentState.data = { ...initialYoutubeSubscriptionsState };
		}
		const getYoutubeSubscriptions = async () => {
			const options = currentState.data;
			set(youtubeSubscriptionsAtom, (prev) => ({ loading: true, data: { ...prev.data, ...options } }));
			try {
				const response: AxiosResponse<YoutubeSubscriptionsResponse> = await axios.get(
					`/youtube/subscriptions/${options.page}/${options.perPage}`
				);
				set(youtubeSubscriptionsAtom, (prev) => ({ loading: false, data: { ...prev.data, ...response.data } }));
				return response.data;
			} catch {
				set(youtubeSubscriptionsAtom, (prev) => ({
					loading: false,
					data: { ...prev.data, subscriptions: [], totalSubscriptions: 0 },
				}));
			}
		};
		if (youtubeAuth.data.email) {
			getYoutubeSubscriptions();
		}
	}
);

youtubeSubscriptionsAtomState.onMount = (setAtom) => setAtom();
