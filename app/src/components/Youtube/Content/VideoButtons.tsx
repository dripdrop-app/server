import { useMemo, useState } from 'react';
import { Alert, Box, IconButton, Snackbar } from '@mui/material';
import { AddToQueue, RemoveFromQueue, ThumbUp, Link, YouTube } from '@mui/icons-material';
import {
	useAddYoutubeVideoLikeMutation,
	useAddYoutubeVideoQueueMutation,
	useDeleteYoutubeVideoLikeMutation,
	useDeleteYoutubeVideoQueueMutation,
} from '../../../api/youtube';
import ConditionalDisplay from '../../ConditionalDisplay';

interface VideoButtonsProps {
	video: YoutubeVideo;
}

const VideoButtons = (props: VideoButtonsProps) => {
	const { video } = props;
	const [open, setOpen] = useState(false);

	const [likeVideo, likedVideoStatus] = useAddYoutubeVideoLikeMutation();
	const [unLikeVideo, unLikedVideoStatus] = useDeleteYoutubeVideoLikeMutation();
	const [queueVideo, queuedVideoStatus] = useAddYoutubeVideoQueueMutation();
	const [unQueueVideo, unQueuedVideoStatus] = useDeleteYoutubeVideoQueueMutation();

	const videoLink = `https://www.youtube.com/watch?v=${video.id}`;

	return useMemo(
		() => (
			<Box>
				<IconButton
					disabled={unLikedVideoStatus.isLoading || likedVideoStatus.isLoading}
					color={video.liked ? 'success' : 'default'}
					onClick={() => {
						if (video.liked) {
							unLikeVideo(video.id);
						} else {
							likeVideo(video.id);
						}
					}}
				>
					<ThumbUp />
				</IconButton>
				<ConditionalDisplay condition={!video.queued}>
					<IconButton
						color="primary"
						disabled={!!video.queued || queuedVideoStatus.isLoading}
						onClick={() => queueVideo(video.id)}
					>
						<AddToQueue />
					</IconButton>
				</ConditionalDisplay>
				<ConditionalDisplay condition={!!video.queued}>
					<IconButton
						color="error"
						disabled={!video.queued || unQueuedVideoStatus.isLoading}
						onClick={() => unQueueVideo(video.id)}
					>
						<RemoveFromQueue />
					</IconButton>
				</ConditionalDisplay>
				<IconButton onClick={() => navigator.clipboard.writeText(videoLink).then(() => setOpen(true))}>
					<Link />
				</IconButton>
				<a href={videoLink} target="_blank" rel="noopener noreferrer">
					<IconButton color="error">
						<YouTube />
					</IconButton>
				</a>
				<Snackbar open={open} autoHideDuration={5000} onClose={() => setOpen(false)}>
					<Alert severity="success">Video Link Copied.</Alert>
				</Snackbar>
			</Box>
		),
		[
			likeVideo,
			likedVideoStatus.isLoading,
			open,
			queueVideo,
			queuedVideoStatus.isLoading,
			unLikeVideo,
			unLikedVideoStatus.isLoading,
			unQueueVideo,
			unQueuedVideoStatus.isLoading,
			video.id,
			video.liked,
			video.queued,
			videoLink,
		]
	);
};

export default VideoButtons;
