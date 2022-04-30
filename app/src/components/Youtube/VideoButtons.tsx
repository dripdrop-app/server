import { useMemo, useState } from 'react';
import { Alert, Box, IconButton, Snackbar } from '@mui/material';
import { AddToQueue, RemoveFromQueue, ThumbUp, Link, YouTube } from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import { useCreateYoutubeVideoLikeMutation, useDeleteYoutubeVideoLikeMutation } from '../../api/youtube';
import { addVideoToQueue, removeVideoFromQueue } from '../../state/youtubeCollections';
import ConditionalDisplay from '../ConditionalDisplay';

interface VideoButtonsProps {
	video: YoutubeVideo;
}

const VideoButtons = (props: VideoButtonsProps) => {
	const { video } = props;
	const [open, setOpen] = useState(false);

	const dispatch = useDispatch();
	const inQueue = useSelector((state: RootState) => {
		return !!state.videoQueue.videos.find((video) => video.id === props.video.id);
	});

	const [likeVideo, likedVideoStatus] = useCreateYoutubeVideoLikeMutation();
	const [unLikeVideo, unLikedVideoStatus] = useDeleteYoutubeVideoLikeMutation();

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
				<ConditionalDisplay condition={!inQueue}>
					<IconButton color="primary" disabled={inQueue} onClick={() => dispatch(addVideoToQueue(video))}>
						<AddToQueue />
					</IconButton>
				</ConditionalDisplay>
				<ConditionalDisplay condition={inQueue}>
					<IconButton color="error" disabled={!inQueue} onClick={() => dispatch(removeVideoFromQueue(video.id))}>
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
			dispatch,
			inQueue,
			likeVideo,
			likedVideoStatus.isLoading,
			open,
			unLikeVideo,
			unLikedVideoStatus.isLoading,
			video,
			videoLink,
		]
	);
};

export default VideoButtons;
