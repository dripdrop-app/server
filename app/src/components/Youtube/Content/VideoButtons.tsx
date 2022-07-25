import { useMemo, useRef, useState } from 'react';
import { Alert, Box, IconButton, Popover, Snackbar, Typography } from '@mui/material';
import { AddToQueue, RemoveFromQueue, ThumbUp, Link, YouTube, RemoveRedEye } from '@mui/icons-material';
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
	const [openCopied, setOpenCopied] = useState(false);
	const [openWatched, setOpenWatched] = useState(false);
	const watchIconRef = useRef<HTMLDivElement>(null);

	const [likeVideo, likedVideoStatus] = useAddYoutubeVideoLikeMutation();
	const [unLikeVideo, unLikedVideoStatus] = useDeleteYoutubeVideoLikeMutation();
	const [queueVideo, queuedVideoStatus] = useAddYoutubeVideoQueueMutation();
	const [unQueueVideo, unQueuedVideoStatus] = useDeleteYoutubeVideoQueueMutation();

	const videoLink = `https://www.youtube.com/watch?v=${video.id}`;
	const watchedDate = video.watched ? new Date(video.watched).toLocaleDateString() : '';

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
				<IconButton onClick={() => navigator.clipboard.writeText(videoLink).then(() => setOpenCopied(true))}>
					<Link />
				</IconButton>
				<a href={videoLink} target="_blank" rel="noopener noreferrer">
					<IconButton color="error">
						<YouTube />
					</IconButton>
				</a>
				<ConditionalDisplay condition={!!video.watched}>
					<Box display="inline" ref={watchIconRef}>
						<IconButton onClick={() => setOpenWatched(true)}>
							<RemoveRedEye />
						</IconButton>
					</Box>
					<Popover
						open={openWatched}
						onClose={() => setOpenWatched(false)}
						anchorEl={watchIconRef.current}
						anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
					>
						<Typography padding={1}>Viewed on {watchedDate}</Typography>
					</Popover>
				</ConditionalDisplay>
				<Snackbar open={openCopied} autoHideDuration={5000} onClose={() => setOpenCopied(false)}>
					<Alert severity="success">Video Link Copied.</Alert>
				</Snackbar>
			</Box>
		),
		[
			likeVideo,
			likedVideoStatus.isLoading,
			openCopied,
			openWatched,
			queueVideo,
			queuedVideoStatus.isLoading,
			unLikeVideo,
			unLikedVideoStatus.isLoading,
			unQueueVideo,
			unQueuedVideoStatus.isLoading,
			video.id,
			video.liked,
			video.queued,
			video.watched,
			videoLink,
			watchedDate,
		]
	);
};

export default VideoButtons;
