import { useMemo } from 'react';
import { Box, Tooltip } from '@mui/material';
import { AddToQueue, RemoveFromQueue, ThumbUp, RemoveRedEye } from '@mui/icons-material';
import { LoadingButton } from '@mui/lab';
import {
	useAddYoutubeVideoLikeMutation,
	useAddYoutubeVideoQueueMutation,
	useDeleteYoutubeVideoLikeMutation,
	useDeleteYoutubeVideoQueueMutation,
} from '../../api/youtube';

interface VideoButtonsProps {
	video: YoutubeVideo;
}

export const YoutubeVideoLikeButton = (props: VideoButtonsProps) => {
	const { video } = props;

	const [likeVideo, likeVideoStatus] = useAddYoutubeVideoLikeMutation();
	const [unLikeVideo, unLikeVideoStatus] = useDeleteYoutubeVideoLikeMutation();

	return useMemo(
		() => (
			<LoadingButton
				loading={likeVideoStatus.isLoading || unLikeVideoStatus.isLoading}
				onClick={() => (video.liked ? unLikeVideo(video.id) : likeVideo(video.id))}
				color={video.liked ? 'success' : 'primary'}
			>
				<ThumbUp />
			</LoadingButton>
		),
		[likeVideo, likeVideoStatus.isLoading, unLikeVideo, unLikeVideoStatus.isLoading, video.id, video.liked]
	);
};

export const YoutubeVideoQueueButton = (props: VideoButtonsProps) => {
	const { video } = props;

	const [queueVideo, queueVideoStatus] = useAddYoutubeVideoQueueMutation();
	const [unQueueVideo, unQueueVideoStatus] = useDeleteYoutubeVideoQueueMutation();

	return useMemo(
		() => (
			<LoadingButton
				loading={queueVideoStatus.isLoading || unQueueVideoStatus.isLoading}
				onClick={() => (video.queued ? unQueueVideo(video.id) : queueVideo(video.id))}
				color={video.queued ? 'error' : 'inherit'}
			>
				<AddToQueue sx={{ display: video.queued ? 'none' : 'block' }} />
				<RemoveFromQueue color="error" sx={{ display: video.queued ? 'block' : 'none' }} />
			</LoadingButton>
		),
		[queueVideo, queueVideoStatus.isLoading, unQueueVideo, unQueueVideoStatus.isLoading, video.id, video.queued]
	);
};

export const YoutubeVideoWatchButton = (props: VideoButtonsProps) => {
	const { video } = props;

	const watchedDate = video.watched ? new Date(video.watched).toLocaleDateString() : '';

	return useMemo(
		() => (
			<Tooltip title={`Watched on ${watchedDate}`}>
				<RemoveRedEye sx={{ display: video.watched ? 'block' : 'none' }} />
			</Tooltip>
		),
		[video.watched, watchedDate]
	);
};

const VideoButtons = (props: VideoButtonsProps) => {
	const { video } = props;

	return useMemo(
		() => (
			<Box>
				<YoutubeVideoLikeButton video={video} />
				<YoutubeVideoQueueButton video={video} />
				<YoutubeVideoWatchButton video={video} />
			</Box>
		),
		[video]
	);
};

export default VideoButtons;
