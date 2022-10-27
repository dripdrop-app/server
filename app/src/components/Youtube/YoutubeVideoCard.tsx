import { useEffect, useMemo, useRef, useState, useCallback } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { Card, CardMedia, CardContent, Typography, Link, Stack, Box, Avatar } from '@mui/material';
import { YoutubeVideoQueueButton, YoutubeVideoWatchButton } from './YoutubeVideoButtons';

interface VideoCardProps {
	video: YoutubeVideo;
}

const VideoCard = (props: VideoCardProps) => {
	const { video } = props;
	const [imageDimensions, setImageDimensions] = useState({ width: 0, height: 0 });
	const [cardHovered, setCardHovered] = useState(false);

	const cardRef = useRef<HTMLDivElement>(null);
	const imageRef = useRef<HTMLImageElement>(null);

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
							<YoutubeVideoWatchButton video={video} />
						</Box>
						<Box sx={{ float: 'right' }}>
							<YoutubeVideoQueueButton video={video} />
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
	}, [cardHovered, imageDimensions.height, imageDimensions.width, video]);
};

export default VideoCard;
