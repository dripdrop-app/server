import { useState, useMemo, Fragment } from 'react';
import {
	Box,
	Button,
	Checkbox,
	Divider,
	FormControlLabel,
	FormGroup,
	IconButton,
	Modal,
	Paper,
	Stack,
	SxProps,
	Theme,
	Typography,
} from '@mui/material';
import { Category, Close } from '@mui/icons-material';
import { useYoutubeVideoCategoriesQuery } from '../../api/youtube';

interface CategorySelectProps extends ChannelBody {
	onChange: (selectedCategories: number[]) => void;
	currentCategories: number[];
	sx?: SxProps<Theme>;
}

const CategorySelect = (props: CategorySelectProps) => {
	const { sx, currentCategories, onChange, channelId } = props;
	const [openModal, setOpenModal] = useState(false);
	const [selectedCategories, setSelectedCategories] = useState<number[]>([]);

	const videoCategoriesStatus = useYoutubeVideoCategoriesQuery({ channelId });

	const categories = useMemo(() => {
		if (videoCategoriesStatus.isSuccess && videoCategoriesStatus.currentData) {
			const { categories } = videoCategoriesStatus.currentData;
			return categories;
		}
		return [];
	}, [videoCategoriesStatus.currentData, videoCategoriesStatus.isSuccess]);

	const RenderCategories = useMemo(
		() =>
			categories.map((category) => {
				const isSelected = !!selectedCategories.find((selectedCategory) => selectedCategory === category.id);
				return (
					<FormControlLabel
						key={category.id}
						control={
							<Checkbox
								checked={isSelected}
								onChange={(e, checked) => {
									if (checked) {
										setSelectedCategories((prevValue) => [...prevValue, category.id]);
									} else {
										setSelectedCategories((prevValue) =>
											prevValue.filter((selectedCategory) => selectedCategory !== category.id)
										);
									}
								}}
							/>
						}
						label={category.name}
					/>
				);
			}),
		[categories, selectedCategories]
	);

	return useMemo(
		() => (
			<Fragment>
				<Button
					sx={sx}
					variant="contained"
					startIcon={<Category />}
					onClick={() => {
						if (currentCategories) {
							setSelectedCategories(currentCategories);
						}
						setOpenModal(true);
					}}
				>
					Categories
				</Button>
				<Modal open={openModal} onClose={() => setOpenModal(false)}>
					<Box
						sx={(theme) => ({
							position: 'absolute',
							padding: 4,
							top: '25%',
							left: '25%',
							width: '50%',
							height: '50%',
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
								<Typography variant="h6">Categories</Typography>
								<IconButton onClick={() => setOpenModal(false)}>
									<Close />
								</IconButton>
							</Stack>
							<Divider />
							<Stack direction="row" flexWrap="wrap" spacing={2}>
								<FormGroup>{RenderCategories}</FormGroup>
							</Stack>
							<Button
								onClick={() => {
									onChange(selectedCategories);
									setOpenModal(false);
								}}
							>
								Confirm
							</Button>
						</Stack>
					</Box>
				</Modal>
			</Fragment>
		),
		[RenderCategories, currentCategories, onChange, openModal, selectedCategories, sx]
	);
};

export default CategorySelect;
