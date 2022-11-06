import { useEffect, useMemo, useRef, useState, useCallback } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { Card, CardMedia, CardContent, Typography, Link, Stack, Box, Chip } from '@mui/material';
import { useYoutubeVideoCategoriesQuery } from '../../api/youtube';
import { VideoQueueButton, VideoWatchButton } from './VideoButtons';

interface VideoCardProps {
	video: YoutubeVideo;
}

const VideoCard = (props: VideoCardProps) => {
	const { video } = props;
	const [imageDimensions, setImageDimensions] = useState({ width: 0, height: 0 });
	const [cardHovered, setCardHovered] = useState(false);
	const cardRef = useRef<HTMLDivElement>(null);
	const imageRef = useRef<HTMLImageElement>(null);

	const videoCategoriesStatus = useYoutubeVideoCategoriesQuery({ channelId: undefined });

	const categories = useMemo(() => {
		if (videoCategoriesStatus.isSuccess && videoCategoriesStatus.currentData) {
			return videoCategoriesStatus.currentData.categories;
		} else if (videoCategoriesStatus.data) {
			return videoCategoriesStatus.data.categories;
		}
		return [];
	}, [videoCategoriesStatus.currentData, videoCategoriesStatus.data, videoCategoriesStatus.isSuccess]);

	const VideoCategoryBadge = useMemo(() => {
		const category = categories.find((category) => video.categoryId === category.id);
		if (category) {
			return <Chip size="small" label={category.name} color="primary" />;
		}
		return null;
	}, [categories, video.categoryId]);

	useEffect(() => {
		const image = imageRef.current;
		const observer = new ResizeObserver((entries) => {
			for (const entry of entries) {
				const rect = entry.target.getBoundingClientRect();
				setImageDimensions({
					width: rect.width,
					height: rect.height,
				});
			}
		});
		if (image) {
			observer.observe(image);
		}
		return () => {
			if (image) {
				observer.unobserve(image);
			}
		};
	}, []);

	const onMouseMove = useCallback((e: MouseEvent) => {
		const card = cardRef.current;
		if (card) {
			const rect = card.getBoundingClientRect();
			if (
				rect.x <= e.clientX &&
				e.clientX <= rect.x + rect.width &&
				rect.y <= e.clientY &&
				e.clientY <= rect.y + rect.height
			) {
				setCardHovered(true);
			} else {
				setCardHovered(false);
			}
		}
	}, []);

	useEffect(() => {
		window.addEventListener('mousemove', onMouseMove);
		return () => window.removeEventListener('mousemove', onMouseMove);
	}, [onMouseMove]);

	return useMemo(() => {
		const publishedAt = new Date(video.publishedAt).toLocaleDateString();
		const channelLink = `/youtube/channel/${video.channelId}`;
		const videoLink = `/youtube/video/${video.id}`;

		return (
			<Card ref={cardRef}>
				<Stack direction="column" position="relative">
					<CardMedia ref={imageRef} component="img" image={video.thumbnail} loading="lazy" />
					<Link component={RouterLink} to={videoLink} sx={{ position: 'absolute' }}>
						<Box
							sx={(theme) => ({
								background: cardHovered ? 'linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0))' : '',
								[theme.breakpoints.down('md')]: {
									background: 'linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0))',
								},
							})}
							height={imageDimensions.height}
							width={imageDimensions.width}
						/>
					</Link>
					<Box position="absolute" bottom="5%" right="5%">
						{VideoCategoryBadge}
					</Box>
					<Box
						sx={(theme) => ({
							display: cardHovered ? 'block' : 'none',
							[theme.breakpoints.down('md')]: {
								display: 'block',
							},
						})}
						position="absolute"
						width="100%"
						alignItems="center"
						padding={2}
					>
						<Box sx={{ float: 'left' }}>
							<VideoWatchButton video={video} />
						</Box>
						<Box sx={{ float: 'right' }}>
							<VideoQueueButton video={video} />
						</Box>
					</Box>
				</Stack>
				<CardContent component={Stack} direction="column" spacing={2}>
					<Typography variant="body1">
						<Link component={RouterLink} to={videoLink}>
							{video.title}
						</Link>
					</Typography>
					<Stack direction="row" spacing={2} flexWrap="wrap">
						<Typography variant="caption">
							<Link component={RouterLink} to={channelLink}>
								{video.channelTitle}
							</Link>
						</Typography>
						<Typography variant="caption">{publishedAt}</Typography>
					</Stack>
				</CardContent>
			</Card>
		);
	}, [VideoCategoryBadge, cardHovered, imageDimensions.height, imageDimensions.width, video]);
};

export default VideoCard;
