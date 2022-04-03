import { BaseQueryApi } from '@reduxjs/toolkit/dist/query/baseQueryTypes';
import { FetchBaseQueryArgs } from '@reduxjs/toolkit/dist/query/fetchBaseQuery';
import { createApi, fetchBaseQuery, FetchArgs } from '@reduxjs/toolkit/query/react';
import { buildWebsocketURL } from '../config';

export const errorParser = (error: ErrorResponse | undefined) => {
	if (error && typeof error.detail === 'string') {
		return error.detail;
	} else if (error && typeof error.detail !== 'string') {
		return error.detail.reduce((msg, error) => {
			const field = error.loc.pop();
			if (field) {
				let message = error.msg.replace('value', field);
				message = message.charAt(0).toLocaleUpperCase() + message.substring(1);
				msg = !msg ? message : `${msg}, ${message}`;
			}
			return msg;
		}, '');
	}
	return error;
};

const customBaseQuery = (options?: FetchBaseQueryArgs) => {
	const fetch = fetchBaseQuery(options);
	return async (args: string | FetchArgs, api: BaseQueryApi, extraOptions: {}) => {
		const response = await fetch(args, api, extraOptions);
		let error;
		if (response.error && response.error.data) {
			error = response.error.data as ErrorResponse;
			error = errorParser(error);
			response.error.data = error;
		}
		return response;
	};
};

const api = createApi({
	baseQuery: customBaseQuery({ baseUrl: '/' }),
	tagTypes: [
		'User',
		'MusicJob',
		'YoutubeAuth',
		'YoutubeVideo',
		'YoutubeVideoCategory',
		'YoutubeVideoQueue',
		'YoutubeSubscription',
		'MusicGrouping',
		'MusicArtwork',
		'MusicTags',
	],
	endpoints: (build) => ({
		checkSession: build.query<User, null>({
			query: () => ({
				url: '/auth/session',
			}),
			providesTags: ['User'],
		}),
		loginOrCreate: build.mutation<User | undefined, { email: string; password: string; login: boolean }>({
			query: ({ email, password, login }) => ({
				url: `/auth/${login ? 'login' : 'create'}`,
				method: 'POST',
				body: { email, password },
			}),
			invalidatesTags: (result, error, args) =>
				args.login && !error ? ['User', 'MusicJob', 'YoutubeSubscription', 'YoutubeVideo', 'YoutubeAuth'] : [],
		}),
		logout: build.mutation<undefined, null>({
			query: () => ({
				url: '/auth/logout',
			}),
			invalidatesTags: (result, error) =>
				!error ? ['User', 'MusicJob', 'YoutubeSubscription', 'YoutubeVideo', 'YoutubeAuth'] : [],
		}),
		grouping: build.query<GroupingResponse, string>({
			query: (youtubeUrl) => ({ url: `/music/grouping`, params: { youtube_url: youtubeUrl } }),
			providesTags: ['MusicGrouping'],
		}),
		artwork: build.query<Artwork, string>({
			query: (artworkUrl) => {
				const searchParams = new URLSearchParams();
				searchParams.append('artwork_url', artworkUrl);
				return { url: `/music/artwork?${searchParams}` };
			},
			providesTags: ['MusicArtwork'],
		}),
		tags: build.query<TagsResponse, File>({
			query: (file) => {
				const formData = new FormData();
				formData.append('file', file);
				return { url: '/music/tags', method: 'POST', body: formData };
			},
			providesTags: ['MusicTags'],
		}),
		jobs: build.query<JobsResponse, null>({
			query: () => '/music/jobs',
			providesTags: (result) => (result ? result.jobs.map((job) => ({ type: 'MusicJob', id: job.id })) : []),
			onCacheEntryAdded: async (arg, { updateCachedData, cacheDataLoaded, cacheEntryRemoved }) => {
				const url = buildWebsocketURL('/music/jobs/listen');
				const ws = new WebSocket(url);
				try {
					await cacheDataLoaded;
					ws.onmessage = (event) => {
						const json = JSON.parse(event.data);
						const type = json.type;
						if (type === 'STARTED') {
							updateCachedData(({ jobs }) => {
								jobs.splice(0, 0, json.job);
							});
						} else if (type === 'COMPLETED') {
							updateCachedData(({ jobs }) => {
								const jobIndex = jobs.findIndex((job) => job.id === json.job.id);
								if (jobIndex !== -1) {
									jobs.splice(jobIndex, 1, json.job);
								}
							});
						}
					};
				} finally {
					await cacheEntryRemoved;
					ws.close();
				}
			},
		}),
		removeJob: build.mutation<undefined, string>({
			query: (jobID) => ({
				url: `/music/jobs/delete/${jobID}`,
				method: 'DELETE',
			}),
			invalidatesTags: (result, error, jobID) => (!error ? [{ type: 'MusicJob', id: jobID }] : []),
		}),
		downloadJob: build.query<Response, string>({
			query: (jobID) => ({
				url: `/music/jobs/download/${jobID}`,
				responseHandler: (response) => Promise.resolve(response),
			}),
		}),
		createFileJob: build.query<undefined, CreateFileJobBody>({
			query: (args) => {
				const formData = new FormData();
				formData.append('file', args.file);
				formData.append('artworkUrl', args.artworkUrl);
				formData.append('title', args.title);
				formData.append('artist', args.artist);
				formData.append('album', args.album);
				if (args.grouping) {
					formData.append('grouping', args.grouping);
				}
				return { url: '/music/jobs/create/file', method: 'POST', body: formData };
			},
		}),
		createYoutubeJob: build.query<undefined, CreateYoutubeJobBody>({
			query: (args) => {
				const formData = new FormData();
				formData.append('youtubeUrl', args.youtubeUrl);
				formData.append('artworkUrl', args.artworkUrl);
				formData.append('title', args.title);
				formData.append('artist', args.artist);
				formData.append('album', args.album);
				if (args.grouping) {
					formData.append('grouping', args.grouping);
				}
				return { url: '/music/jobs/create/youtube', method: 'POST', body: formData };
			},
		}),
		checkYoutubeAuth: build.query<YoutubeAuthState, null>({
			query: () => ({ url: '/youtube/account' }),
			providesTags: ['YoutubeAuth'],
		}),
		getOauthLink: build.query<string, null>({
			query: () => ({ url: '/youtube/oauth' }),
		}),
		youtubeVideoCategories: build.query<YoutubeVideoCategoriesResponse, ChannelBody>({
			query: ({ channelId }) => {
				let url = '/youtube/videos/categories';
				const searchParams = new URLSearchParams();
				if (channelId) {
					searchParams.append('channel_id', channelId);
				}
				if (searchParams.toString()) {
					url += `?${searchParams}`;
				}
				return { url };
			},
			providesTags: (result) =>
				result?.categories.map((category) => ({ type: 'YoutubeVideoCategory', id: category.id })) ?? [],
		}),
		youtubeVideos: build.query<YoutubeVideosResponse, YoutubeVideoBody>({
			query: ({ perPage, page, channelId, selectedCategories }) => {
				let url = `/youtube/videos/${page}/${perPage}`;
				const searchParams = new URLSearchParams();
				if (channelId) {
					searchParams.append('channel_id', channelId);
				}
				if (selectedCategories) {
					selectedCategories.forEach((category) => searchParams.append('video_categories', category.toString()));
				}
				if (searchParams.toString()) {
					url += `?${searchParams}`;
				}
				return { url };
			},
			providesTags: (result) => result?.videos.map((video) => ({ type: 'YoutubeVideo', id: video.id })) ?? [],
		}),
		youtubeSubscriptions: build.query<YoutubeSubscriptionsResponse, YoutubeSubscriptionBody>({
			query: ({ perPage, page, channelId }) => {
				let url = `/youtube/subscriptions/${page}/${perPage}`;
				const searchParams = new URLSearchParams();
				if (channelId) {
					searchParams.append('channel_id', channelId);
				}
				if (searchParams.toString()) {
					url += `?${searchParams}`;
				}
				return { url };
			},
			providesTags: (result) =>
				result?.subscriptions.map((subscription) => ({ type: 'YoutubeSubscription', id: subscription.id })) ?? [],
		}),
	}),
});

export default api;
export const {
	useCheckSessionQuery,
	useLoginOrCreateMutation,
	useLogoutMutation,
	useLazyArtworkQuery,
	useLazyGroupingQuery,
	useLazyTagsQuery,
	useLazyCreateFileJobQuery,
	useLazyCreateYoutubeJobQuery,
	useJobsQuery,
	useRemoveJobMutation,
	useLazyDownloadJobQuery,
	useCheckYoutubeAuthQuery,
	useLazyGetOauthLinkQuery,
	useYoutubeVideoCategoriesQuery,
	useYoutubeVideosQuery,
	useYoutubeSubscriptionsQuery,
} = api;
