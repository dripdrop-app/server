import { useRecoilState, useRecoilValueLoadable } from 'recoil';
import {
	Box,
	Button,
	Chip,
	CircularProgress,
	Container,
	Menu,
	MenuItem,
	Pagination,
	Stack,
	ToggleButton,
	ToggleButtonGroup,
} from '@mui/material';
import { ArrowDropDown } from '@mui/icons-material';
import { videoCategoriesSelector, videoOptionsState, videosSelector } from '../../state/YoutubeCollections';
import CustomGrid from './CustomGrid';
import YoutubeVideoCard from './YoutubeVideoCard';
import { useRef, useState } from 'react';

const VideosView = (props: { channelID: string | null }) => {
	const buttonRef = useRef<HTMLButtonElement | null>(null);
	const [showMenu, setShowMenu] = useState(false);

	const [videoOptions, updateVideoOptions] = useRecoilState(videoOptionsState(props.channelID));
	const videosState = useRecoilValueLoadable(videosSelector(props.channelID));
	const videoCategoriesState = useRecoilValueLoadable(videoCategoriesSelector(props.channelID));

	if (
		videosState.state === 'loading' ||
		videosState.state === 'hasError' ||
		videoCategoriesState.state === 'loading' ||
		videoCategoriesState.state === 'hasError'
	) {
		return (
			<Stack justifyContent="center" direction="row" sx={{ my: 5 }}>
				<CircularProgress />
			</Stack>
		);
	}

	const { categories } = videoCategoriesState.contents;
	const { videos, totalVideos } = videosState.contents;
	const { perPage, page, selectedCategories } = videoOptions;

	const SelectedCategoryChip = (id: number) => {
		const category = categories.find((category: YoutubeVideoCategory) => category.id === id);
		if (category) {
			return (
				<Chip
					sx={{ m: 0.5 }}
					color="primary"
					key={category.id}
					label={category.name}
					onDelete={() =>
						updateVideoOptions({
							...videoOptions,
							selectedCategories: selectedCategories.filter((c) => c !== category.id),
						})
					}
				/>
			);
		}
		return null;
	};

	const CategoryList = () => {
		const sortedCategories = [...categories].sort((a, b) => (a.name > b.name ? 1 : -1));
		return sortedCategories.map((category) => {
			return (
				<MenuItem
					key={category.id}
					value={category.id}
					onClick={() => {
						updateVideoOptions({ ...videoOptions, selectedCategories: [...selectedCategories, category.id] });
						setShowMenu(false);
					}}
				>
					{category.name}
				</MenuItem>
			);
		});
	};

	return (
		<Container sx={{ my: 5 }}>
			<Stack sx={{ my: 2 }} direction="row" alignItems="center" spacing={2}>
				<Button variant="contained" ref={buttonRef} onClick={() => setShowMenu(true)}>
					Categories
					<ArrowDropDown />
				</Button>
				<Menu anchorEl={buttonRef.current} open={showMenu} onClose={() => setShowMenu(false)}>
					{CategoryList()}
				</Menu>
				<Stack direction="row" flexWrap="wrap">
					{selectedCategories.map((id) => SelectedCategoryChip(id))}
				</Stack>
				<Button variant="contained" onClick={() => updateVideoOptions({ ...videoOptions, selectedCategories: [] })}>
					Reset
				</Button>
				<Box sx={{ flexGrow: 1 }} />
				<ToggleButtonGroup
					exclusive
					value={perPage}
					onChange={(e, v) => updateVideoOptions({ ...videoOptions, perPage: v })}
				>
					{([10, 25, 50] as PageState['perPage'][]).map((v) => (
						<ToggleButton key={v} value={v}>
							{v}
						</ToggleButton>
					))}
				</ToggleButtonGroup>
			</Stack>
			<CustomGrid
				items={videos}
				renderItem={(video, selected) => <YoutubeVideoCard selected={selected} video={video} />}
			/>
			<Stack direction="row" sx={{ my: 5 }} justifyContent="center">
				<Pagination
					page={page}
					onChange={(e, page) => updateVideoOptions({ ...videoOptions, page })}
					count={Math.ceil(totalVideos / perPage)}
					color="primary"
				/>
			</Stack>
		</Container>
	);
};

export default VideosView;
