import api from '.';
import { buildWebsocketURL } from '../config';

const musicApi = api.injectEndpoints({
	endpoints: (build) => ({
		grouping: build.query<GroupingResponse, string>({
			query: (youtubeUrl) => ({ url: `/music/grouping`, params: { youtube_url: youtubeUrl } }),
			providesTags: ['MusicGrouping'],
		}),
		artwork: build.query<Artwork, string>({
			query: (artworkUrl) => ({ url: `/music/artwork`, params: { artwork_url: artworkUrl } }),
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
		jobs: build.query<JobsResponse, PageBody>({
			query: ({ page, perPage }) => `/music/jobs/${page}/${perPage}`,
			onCacheEntryAdded: async (args, { cacheDataLoaded, cacheEntryRemoved, dispatch }) => {
				const url = buildWebsocketURL('/music/jobs/listen');
				const ws = new WebSocket(url);
				try {
					await cacheDataLoaded;
					ws.onmessage = (event) => {
						const json = JSON.parse(event.data);
						const type = json.type;
						if (type === 'STARTED') {
							dispatch(musicApi.util.invalidateTags(['MusicJob']));
						} else if (type === 'COMPLETED') {
							dispatch(musicApi.util.invalidateTags([{ type: 'MusicJob', id: json.job.id }]));
						}
					};
				} finally {
					await cacheEntryRemoved;
					ws.close();
				}
			},
			providesTags: (result) => {
				if (result) {
					const { jobs } = result;
					return jobs.map((job) => ({ type: 'MusicJob', id: job.id }));
				}
				return [];
			},
		}),
		removeJob: build.mutation<undefined, string>({
			query: (jobID) => ({
				url: `/music/jobs/delete/${jobID}`,
				method: 'DELETE',
			}),
			invalidatesTags: (result, error, jobID) => {
				if (!error) {
					return [{ type: 'MusicJob', id: jobID }];
				}
				return [];
			},
		}),
		downloadJob: build.query<DownloadResponse, string>({
			query: (jobID) => ({
				url: `/music/jobs/download/${jobID}`,
				providesTags: ['MusicDownload'],
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
	}),
});

export default musicApi;
export const {
	useLazyArtworkQuery,
	useLazyGroupingQuery,
	useLazyTagsQuery,
	useLazyCreateFileJobQuery,
	useLazyCreateYoutubeJobQuery,
	useJobsQuery,
	useRemoveJobMutation,
	useLazyDownloadJobQuery,
} = musicApi;
