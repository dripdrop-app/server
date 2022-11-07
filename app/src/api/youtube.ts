import api from '.';

const youtubeApi = api.injectEndpoints({
	endpoints: (build) => ({
		checkYoutubeAuth: build.query<YoutubeAuthState, void>({
			query: () => ({ url: '/youtube/account' }),
			providesTags: ['YoutubeAuth'],
		}),
		getOauthLink: build.query<string, void>({
			query: () => ({ url: '/youtube/oauth', responseHandler: (response) => response.text() }),
		}),
		youtubeVideoCategories: build.query<YoutubeVideoCategoriesResponse, ChannelBody>({
			query: ({ channelId }) => ({ url: '/youtube/videos/categories', params: { channel_id: channelId } }),
			providesTags: (result) => {
				if (result) {
					return result.categories.map((category) => ({ type: 'YoutubeVideoCategory', id: category.id }));
				}
				return [];
			},
		}),
		youtubeVideo: build.query<YoutubeVideoResponse, YoutubeVideoBody>({
			query: ({ videoId, relatedLength }) => ({
				url: '/youtube/videos',
				params: { video_id: videoId, related_videos_length: relatedLength },
			}),
			providesTags: (result) => {
				if (result) {
					return [{ type: 'YoutubeVideo', id: result.video.id }].concat(
						result.relatedVideos.map((video) => ({ type: 'YoutubeVideo', id: video.id }))
					);
				}
				return [];
			},
		}),
		youtubeVideos: build.query<YoutubeVideosResponse, YoutubeVideosBody>({
			query: ({ perPage, page, channelId, selectedCategories, likedOnly, queuedOnly }) => ({
				url: `/youtube/videos/${page}/${perPage}`,
				params: {
					channel_id: channelId,
					video_categories: selectedCategories.length === 0 ? undefined : selectedCategories,
					liked_only: likedOnly,
					queued_only: queuedOnly,
				},
			}),
			providesTags: (result, error, args) => {
				if (result) {
					const tags = [];
					if (args.likedOnly) {
						tags.push({ type: 'YoutubeVideoLike' });
					}
					if (args.queuedOnly) {
						tags.push({ type: 'YoutubeVideoQueue' });
					}
					return tags.concat(result.videos.map((video) => ({ type: 'YoutubeVideo', id: video.id })));
				}
				return [];
			},
		}),
		youtubeSubscriptions: build.query<YoutubeSubscriptionsResponse, YoutubeSubscriptionBody>({
			query: ({ perPage, page, channelId }) => ({
				url: `/youtube/subscriptions/${page}/${perPage}`,
				params: { channel_id: channelId },
			}),
			providesTags: (result) => {
				if (result) {
					return result.subscriptions.map((subscription) => ({ type: 'YoutubeSubscription', id: subscription.id }));
				}
				return [];
			},
		}),
		addYoutubeVideoLike: build.mutation<undefined, string>({
			query: (videoId) => ({ url: `/youtube/videos/like`, params: { video_id: videoId }, method: 'PUT' }),
			invalidatesTags: (result, error, videoId) => {
				if (!error) {
					return [{ type: 'YoutubeVideo', id: videoId }, { type: 'YoutubeVideoLike' }];
				}
				return [];
			},
		}),
		deleteYoutubeVideoLike: build.mutation<undefined, string>({
			query: (videoId) => ({
				url: `/youtube/videos/like`,
				params: { video_id: videoId },
				method: 'DELETE',
			}),
			invalidatesTags: (result, error, videoId) => {
				if (!error) {
					return [{ type: 'YoutubeVideo', id: videoId }, { type: 'YoutubeVideoLike' }];
				}
				return [];
			},
		}),
		addYoutubeVideoQueue: build.mutation<undefined, string>({
			query: (videoId) => ({
				url: `/youtube/videos/queue`,
				params: { video_id: videoId },
				method: 'PUT',
			}),
			invalidatesTags: (result, error, videoId) => {
				if (!error) {
					return [
						{ type: 'YoutubeVideo', id: videoId },
						{ type: 'YoutubeVideoQueue' },
						{ type: 'YoutubeVideoQueueIndex' },
					];
				}
				return [];
			},
		}),
		deleteYoutubeVideoQueue: build.mutation<undefined, string>({
			query: (videoId) => ({
				url: `/youtube/videos/queue`,
				params: { video_id: videoId },
				method: 'DELETE',
			}),
			invalidatesTags: (result, error, videoId) => {
				if (!error) {
					return [
						{ type: 'YoutubeVideo', id: videoId },
						{ type: 'YoutubeVideoQueue' },
						{ type: 'YoutubeVideoQueueIndex' },
					];
				}
				return [];
			},
		}),
		addYoutubeVideoWatch: build.mutation<undefined, string>({
			query: (videoId) => ({
				url: `/youtube/videos/watch`,
				params: { video_id: videoId },
				method: 'PUT',
			}),
			invalidatesTags: (result, error, videoId) => {
				if (!error) {
					return [{ type: 'YoutubeVideo', id: videoId }];
				}
				return [];
			},
		}),
		youtubeVideoQueue: build.query<YoutubeVideoQueueResponse, number>({
			query: (index) => ({ url: `/youtube/videos/queue`, params: { index }, method: 'GET' }),
			providesTags: (result) => {
				const tags = [{ type: 'YoutubeVideoQueueIndex' }] as any[];
				if (result) {
					tags.push({ type: 'YoutubeVideo', id: result.currentVideo.id });
				}
				return tags;
			},
		}),
		youtubeChannel: build.query<YoutubeChannel, string>({
			query: (channelID) => ({ url: '/youtube/channels', params: { channel_id: channelID }, method: 'GET' }),
			providesTags: (result) => {
				if (result) {
					return [{ type: 'YoutubeChannel', id: result.id }];
				}
				return [];
			},
		}),
	}),
});

export default youtubeApi;
export const {
	useCheckYoutubeAuthQuery,
	useLazyGetOauthLinkQuery,
	useYoutubeVideoCategoriesQuery,
	useYoutubeVideoQuery,
	useYoutubeVideosQuery,
	useYoutubeVideoQueueQuery,
	useYoutubeSubscriptionsQuery,
	useAddYoutubeVideoLikeMutation,
	useDeleteYoutubeVideoLikeMutation,
	useAddYoutubeVideoQueueMutation,
	useDeleteYoutubeVideoQueueMutation,
	useYoutubeChannelQuery,
	useAddYoutubeVideoWatchMutation,
} = youtubeApi;
