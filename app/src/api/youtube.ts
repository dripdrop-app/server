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
				result ? result.categories.map((category) => ({ type: 'YoutubeVideoCategory', id: category.id })) : [],
		}),
		youtubeVideo: build.query<YoutubeVideoResponse, YoutubeVideoBody>({
			query: ({ videoId, relatedLength }) => ({
				url: `/youtube/video/${videoId}?related_videos_length=${relatedLength}`,
			}),
			providesTags: (result, error, args) =>
				result
					? [{ type: 'YoutubeVideo', id: result.video.id }].concat(
							result.relatedVideos.map((video) => ({ type: 'YoutubeVideo', id: video.id }))
					  )
					: [],
		}),
		youtubeVideos: build.query<YoutubeVideosResponse, YoutubeVideosBody>({
			query: ({ perPage, page, channelId, selectedCategories, likedOnly }) => {
				let url = `/youtube/videos/${page}/${perPage}`;
				const searchParams = new URLSearchParams();
				if (channelId) {
					searchParams.append('channel_id', channelId);
				}
				if (selectedCategories) {
					selectedCategories.forEach((category) => searchParams.append('video_categories', category.toString()));
				}
				if (likedOnly) {
					searchParams.append('liked_only', likedOnly.toString());
				}
				if (searchParams.toString()) {
					url += `?${searchParams}`;
				}
				return { url };
			},
			providesTags: (result, error, args) =>
				result ? result.videos.map((video) => ({ type: 'YoutubeVideo', id: video.id })) : [],
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
			providesTags: (result) => {
				if (result) {
					result.subscriptions.map((subscription) => ({ type: 'YoutubeSubscription', id: subscription.id }));
				}
				return [];
			},
		}),
		createYoutubeVideoLike: build.mutation<undefined, string>({
			query: (videoId) => ({ url: `/youtube/videos/like?video_id=${videoId}`, method: 'PUT' }),
			invalidatesTags: (result, error, videoId) => (!error ? [{ type: 'YoutubeVideo', id: videoId }] : []),
		}),
		deleteYoutubeVideoLike: build.mutation<undefined, string>({
			query: (videoId) => ({ url: `/youtube/videos/unlike?video_id=${videoId}`, method: 'PUT' }),
			invalidatesTags: (result, error, videoId) => (!error ? [{ type: 'YoutubeVideo', id: videoId }] : []),
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
	useYoutubeSubscriptionsQuery,
	useCreateYoutubeVideoLikeMutation,
	useDeleteYoutubeVideoLikeMutation,
} = youtubeApi;
