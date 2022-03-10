import React, { useRef, useState } from 'react';
import { useRecoilState, useRecoilValueLoadable } from 'recoil';
import { Button, Chip, Container, Menu, MenuItem, Pagination, Skeleton, Stack } from '@mui/material';
import { ArrowDropDown } from '@mui/icons-material';
import { videoCategoriesSelector, videoOptionsState, videosSelector } from '../../state/YoutubeCollections';
import CustomGrid from './CustomGrid';
import YoutubeVideoCard from './YoutubeVideoCard';

interface BaseProps {
	channelID: string | null;
}

const CategoriesSelect = (props: BaseProps) => {
	const buttonRef = useRef<HTMLButtonElement | null>(null);
	const [showMenu, setShowMenu] = useState(false);

	const [videoOptions, updateVideoOptions] = useRecoilState(videoOptionsState(props.channelID));
	const videoCategoriesState = useRecoilValueLoadable(videoCategoriesSelector(props.channelID));

	if (videoCategoriesState.state === 'loading' || videoCategoriesState.state === 'hasError') {
		return (
			<Stack justifyContent="center" direction="row" sx={{ my: 5 }}>
				<Skeleton variant="text" />
			</Stack>
		);
	}

	const { categories } = videoCategoriesState.contents;
	const { selectedCategories } = videoOptions;

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
		const sortedCategories = [...categories]
			.sort((a, b) => (a.name > b.name ? 1 : -1))
			.filter((c) => selectedCategories.indexOf(c.id) === -1);
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
		<React.Fragment>
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
		</React.Fragment>
	);
};

const VideosDisplay = (props: BaseProps) => {
	const [videoOptions, updateVideoOptions] = useRecoilState(videoOptionsState(props.channelID));
	const videosState = useRecoilValueLoadable(videosSelector(props.channelID));

	const { perPage, page } = videoOptions;

	if (videosState.state === 'loading' || videosState.state === 'hasError') {
		return (
			<Stack justifyContent="center" direction="row" sx={{ my: 5 }}>
				<CustomGrid
					items={Array(perPage).fill(0)}
					renderItem={(i, selected) => <Skeleton width="100%" height="10em" variant="rectangular" />}
				/>
			</Stack>
		);
	}

	const { videos, totalVideos } = videosState.contents;

	return (
		<React.Fragment>
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
		</React.Fragment>
	);
};

const VideosView = (props: BaseProps) => {
	return (
		<Container sx={{ my: 5 }}>
			<Stack sx={{ my: 2 }} direction="row" alignItems="center" spacing={2}>
				<CategoriesSelect channelID={props.channelID} />
			</Stack>
			<VideosDisplay channelID={props.channelID} />
		</Container>
	);
};

export default VideosView;
