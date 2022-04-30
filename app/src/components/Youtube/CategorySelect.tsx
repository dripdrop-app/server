import { Chip, FormControl, InputLabel, MenuItem, Select, Stack } from '@mui/material';
import { useCallback, useMemo, useState } from 'react';
import { useYoutubeVideoCategoriesQuery } from '../../api';

interface CategorySelectProps {
	channelID?: string;
	onChange: (newCategories: number[]) => void;
}

const CategorySelect = (props: CategorySelectProps) => {
	const { onChange, channelID } = props;
	const [selectedCategories, setSelectedCategories] = useState<number[]>([]);

	const videoCategoriesStatus = useYoutubeVideoCategoriesQuery({ channelId: channelID });

	const categories = useMemo(
		() =>
			videoCategoriesStatus.isSuccess && videoCategoriesStatus.currentData
				? videoCategoriesStatus.currentData.categories
				: [],
		[videoCategoriesStatus.currentData, videoCategoriesStatus.isSuccess]
	);

	const CategoryList = useMemo(() => {
		return [...categories]
			.sort((a, b) => (a.name > b.name ? 1 : -1))
			.map((category) => ({
				key: category.id,
				text: category.name,
				value: category.id,
			}));
	}, [categories]);

	const getCategory = useCallback(
		(categoryId: number) => {
			return CategoryList.find((category) => category.value === categoryId);
		},
		[CategoryList]
	);

	return useMemo(
		() => (
			<FormControl fullWidth>
				<InputLabel id="categories">Categories</InputLabel>
				<Select
					labelId="categories"
					label="Categories"
					renderValue={(selected) => (
						<Stack direction="row" flexWrap="wrap" spacing={1}>
							{selected.map((s) => {
								const category = getCategory(s);
								if (category) {
									return <Chip key={s} label={category.text} />;
								}
								return null;
							})}
						</Stack>
					)}
					multiple
					value={selectedCategories}
					onChange={(e) => {
						if (typeof e.target.value === 'string') {
							const newCategories = e.target.value.split(',').map(parseInt);
							setSelectedCategories(newCategories);
							onChange(newCategories);
						} else {
							setSelectedCategories(e.target.value);
							onChange(e.target.value);
						}
					}}
				>
					{CategoryList.map((category) => (
						<MenuItem key={category.key} value={category.value}>
							{category.text}
						</MenuItem>
					))}
				</Select>
			</FormControl>
		),
		[CategoryList, getCategory, onChange, selectedCategories]
	);
};

export default CategorySelect;
