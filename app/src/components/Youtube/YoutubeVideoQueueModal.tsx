import { useCallback, useEffect, useMemo, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
	List,
	Paper,
	ListItem,
	ListItemButton,
	Stack,
	ListItemAvatar,
	Avatar,
	ListItemText,
	CircularProgress,
	Box,
	Modal,
	Button,
	Typography,
	Pagination,
	IconButton,
} from '@mui/material';
import { Close, MenuOpen } from '@mui/icons-material';
import { setVideoQueueIndex } from '../../state/youtube';
import { useYoutubeVideosQuery } from '../../api/youtube';
import { YoutubeVideoQueueButton } from './YoutubeVideoButtons';
import YoutubeVideosPage from './YoutubeVideosPage';

interface YoutubeVideoQueueModalProps {
	currentVideo: YoutubeVideo;
}

const YoutubeVideoQueueModal = (props: YoutubeVideoQueueModalProps) => {
	const { currentVideo } = props;

	const [openModal, setOpenModal] = useState(false);
	const [filter, setFilter] = useState<YoutubeVideosBody>({
		page: 1,
		perPage: 50,
		queuedOnly: true,
		selectedCategories: [],
	});

	const dispatch = useDispatch();
	const { queueIndex } = useSelector((state: RootState) => ({
		queueIndex: state.youtube.queue.index,
	}));

	const videosStatus = useYoutubeVideosQuery(filter);

	const totalPages = useMemo(() => {
		if (videosStatus.isSuccess && videosStatus.currentData) {
			return videosStatus.currentData.totalPages;
		} else if (videosStatus.data) {
			return videosStatus.data.totalPages;
		}
		return 1;
	}, [videosStatus.currentData, videosStatus.data, videosStatus.isSuccess]);

	const getVideoIndex = useCallback(
		(index: number) => (filter.page - 1) * filter.perPage + index + 1,
		[filter.page, filter.perPage]
	);

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
				<Modal open={openModal} onClose={() => setOpenModal(false)}>
					<Box
						sx={(theme) => ({
							position: 'absolute',
							padding: 4,
							top: '10%',
							left: '10%',
							width: '80%',
							height: '80%',
							overflow: 'scroll',
							[theme.breakpoints.down('md')]: {
								padding: 2,
								top: 0,
								left: 0,
								width: '100%',
								height: '100%',
							},
						})}
						component={Paper}
					>
						<Stack direction="column" spacing={2}>
							<Stack direction="row" justifyContent="space-between">
								<Typography variant="h6">Queue</Typography>
								<IconButton onClick={() => setOpenModal(false)}>
									<Close />
								</IconButton>
							</Stack>
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
								<YoutubeVideosPage
									page={filter.page}
									perPage={filter.perPage}
									queuedOnly={filter.queuedOnly}
									selectedCategories={filter.selectedCategories}
									renderItem={(video, index) => (
										<ListItem
											divider
											sx={{
												border: (theme) =>
													video.id === currentVideo.id ? `1px solid ${theme.palette.primary.dark}` : '',
											}}
										>
											<ListItemButton
												onClick={() => {
													console.log(getVideoIndex(index));
													dispatch(setVideoQueueIndex(getVideoIndex(index)));
													setOpenModal(false);
												}}
											>
												<Stack direction="row" flexWrap="wrap">
													<Stack direction="row" flexWrap="wrap" alignItems="center">
														<ListItemAvatar>
															<Avatar alt={video.title} src={video.thumbnail} />
														</ListItemAvatar>
														<ListItemText primary={video.title} secondary={video.channelTitle} />
													</Stack>
												</Stack>
											</ListItemButton>
											<YoutubeVideoQueueButton video={video} />
										</ListItem>
									)}
									renderLoading={() => (
										<Stack direction="row" justifyContent="center">
											<CircularProgress />
										</Stack>
									)}
								/>
							</List>
							<Stack direction="row" justifyContent="center">
								<Pagination
									page={filter.page}
									count={totalPages}
									color="primary"
									shape="rounded"
									onChange={(e, newPage) => setFilter((prevState) => ({ ...prevState, page: newPage }))}
								/>
							</Stack>
						</Stack>
					</Box>
				</Modal>
			</Box>
		),
		[
			openModal,
			filter.page,
			filter.perPage,
			filter.queuedOnly,
			filter.selectedCategories,
			totalPages,
			currentVideo.id,
			getVideoIndex,
			dispatch,
		]
	);
};

export default YoutubeVideoQueueModal;
