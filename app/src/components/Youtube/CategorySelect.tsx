import { useState, useMemo } from 'react';
import {
	Box,
	Button,
	Checkbox,
	Dialog,
	DialogActions,
	DialogContent,
	DialogTitle,
	FormControlLabel,
	FormGroup,
	IconButton,
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
			return videoCategoriesStatus.currentData.categories;
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
			<Box>
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
				<Dialog open={openModal} onClose={() => setOpenModal(false)} scroll="paper" fullWidth maxWidth="md">
					<DialogTitle>
						<Stack direction="row" alignItems="center" justifyContent="space-between">
							<Typography variant="h6">Categories</Typography>
							<IconButton onClick={() => setOpenModal(false)}>
								<Close />
							</IconButton>
						</Stack>
					</DialogTitle>
					<DialogContent dividers>
						<Stack direction="row" flexWrap="wrap" spacing={2}>
							<FormGroup>{RenderCategories}</FormGroup>
						</Stack>
					</DialogContent>
					<DialogActions>
						<Button
							variant="contained"
							onClick={() => {
								onChange(selectedCategories);
								setOpenModal(false);
							}}
						>
							Confirm
						</Button>
					</DialogActions>
				</Dialog>
			</Box>
		),
		[RenderCategories, currentCategories, onChange, openModal, selectedCategories, sx]
	);
};

export default CategorySelect;
