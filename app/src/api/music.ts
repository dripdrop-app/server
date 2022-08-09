import api from '.';
import { buildWebsocketURL } from '../config';
import { addJob, addJobs, removeJob, updateJob } from '../state/music';

const musicApi = api.injectEndpoints({
	endpoints: (build) => ({
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
		jobs: build.query<JobsResponse, {}>({
			query: () => '/music/jobs',
			onCacheEntryAdded: async (arg, { cacheDataLoaded, cacheEntryRemoved, dispatch }) => {
				const url = buildWebsocketURL('/music/jobs/listen');
				const ws = new WebSocket(url);
				try {
					const response = await cacheDataLoaded;
					const jobs = response.data.jobs;
					dispatch(addJobs(jobs));

					ws.onmessage = (event) => {
						const json = JSON.parse(event.data);
						const type = json.type;
						if (type === 'STARTED') {
							dispatch(addJob(json.job));
						} else if (type === 'COMPLETED') {
							dispatch(updateJob(json.job));
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
			onQueryStarted: async (jobID, { queryFulfilled, dispatch }) => {
				try {
					await queryFulfilled;
					dispatch(removeJob(jobID));
				} catch {}
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
