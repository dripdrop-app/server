import { useEffect, useMemo, useState } from 'react';
import {
	List,
	ListItem,
	ListItemButton,
	Stack,
	ListItemAvatar,
	Avatar,
	ListItemText,
	CircularProgress,
	Box,
	Button,
	Typography,
	Pagination,
	IconButton,
	Dialog,
	DialogTitle,
	DialogContent,
} from '@mui/material';
import { Close, MenuOpen } from '@mui/icons-material';
import { useYoutubeVideosQuery } from '../../api/youtube';
import { VideoQueueButton } from './VideoButtons';
import VideosPage from './VideosPage';

interface VideoQueueModalProps {
	currentVideo: YoutubeVideo | null;
	queueIndex: number;
	setQueueIndex: (newIndex: number) => void;
}

const VideoQueueModal = (props: VideoQueueModalProps) => {
	const { currentVideo, queueIndex, setQueueIndex } = props;

	const [openModal, setOpenModal] = useState(false);
	const [filter, setFilter] = useState<YoutubeVideosBody>({
		page: 1,
		perPage: 50,
		queuedOnly: true,
		selectedCategories: [],
	});

	const videosStatus = useYoutubeVideosQuery(filter);

	const totalPages = useMemo(() => {
		if (videosStatus.isSuccess && videosStatus.currentData) {
			return videosStatus.currentData.totalPages;
		} else if (videosStatus.data) {
			return videosStatus.data.totalPages;
		}
		return 1;
	}, [videosStatus.currentData, videosStatus.data, videosStatus.isSuccess]);

	useEffect(() => {
		const currentVideoPage = Math.ceil(queueIndex / filter.perPage);
		setFilter((prevState) => ({ ...prevState, page: currentVideoPage }));
	}, [filter.perPage, queueIndex]);

	return useMemo(
		() => (
			<Box>
				<Button
					variant="contained"
					sx={{ borderRadius: 0 }}
					onClick={() => setOpenModal(true)}
					startIcon={<MenuOpen />}
				>
					Queue
				</Button>
				<Dialog open={openModal} onClose={() => setOpenModal(false)} fullWidth maxWidth="md">
					<DialogTitle>
						<Stack direction="row" alignItems="center" justifyContent="space-between">
							<Typography variant="h6">Queue</Typography>
							<IconButton onClick={() => setOpenModal(false)}>
								<Close />
							</IconButton>
						</Stack>
					</DialogTitle>
					<DialogContent dividers>
						<List
							disablePadding
							sx={(theme) => ({
								overflow: 'scroll',
								height: '65vh',
								[theme.breakpoints.down('md')]: {
									height: '80vh',
								},
							})}
						>
							<VideosPage
								page={filter.page}
								perPage={filter.perPage}
								queuedOnly={filter.queuedOnly}
								selectedCategories={filter.selectedCategories}
								renderItem={(video, index) => (
									<ListItem
										divider
										sx={{
											backgroundColor: (theme) => (video.id === currentVideo?.id ? theme.palette.primary.main : ''),
										}}
									>
										<ListItemButton
											onClick={() => {
												setQueueIndex((filter.page - 1) * filter.perPage + index + 1);
												setOpenModal(false);
											}}
										>
											<Stack direction="row" alignItems="center">
												<ListItemAvatar>
													<Avatar alt={video.title} src={video.thumbnail} />
												</ListItemAvatar>
												<Stack direction="column">
													<ListItemText primary={video.title} secondary={video.channelTitle} />
													<ListItemText
														sx={{ display: video.id === currentVideo?.id ? 'block' : 'none' }}
														primary="Now Playing"
													/>
												</Stack>
											</Stack>
										</ListItemButton>
										<VideoQueueButton video={video} />
									</ListItem>
								)}
								renderLoading={() => (
									<Stack direction="row" justifyContent="center">
										<CircularProgress />
									</Stack>
								)}
							/>
						</List>
					</DialogContent>
					<Stack direction="row" justifyContent="center" padding={2}>
						<Pagination
							page={filter.page}
							count={totalPages}
							color="primary"
							shape="rounded"
							onChange={(e, newPage) => setFilter((prevState) => ({ ...prevState, page: newPage }))}
						/>
					</Stack>
				</Dialog>
			</Box>
		),
		[
			openModal,
			filter.page,
			filter.perPage,
			filter.queuedOnly,
			filter.selectedCategories,
			totalPages,
			currentVideo,
			setQueueIndex,
		]
	);
};

export default VideoQueueModal;
