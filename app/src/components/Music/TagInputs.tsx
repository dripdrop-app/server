import { useMemo } from 'react';
import { Grid, TextField } from '@mui/material';
import { useSelector, useDispatch } from 'react-redux';
import { updateForm } from '../../state/music';

const TagInputs = () => {
	const dispatch = useDispatch();
	const { title, artist, album, grouping, groupingLoading } = useSelector((state: RootState) => {
		let groupingLoading = false;
		for (const query in state.api.queries) {
			if (query.includes('grouping')) {
				const call = state.api.queries[query];
				groupingLoading = call?.status === 'pending' ?? groupingLoading;
			}
		}
		return {
			title: state.music.form.title,
			artist: state.music.form.artist,
			album: state.music.form.album,
			grouping: state.music.form.grouping,
			groupingLoading,
		};
	});

	return useMemo(
		() => (
			<Grid container spacing={2} alignItems="center">
				<Grid item>
					<TextField
						fullWidth
						label="Title"
						value={title}
						onChange={(e) => dispatch(updateForm({ title: e.target.value }))}
					/>
				</Grid>
				<Grid item>
					<TextField
						fullWidth
						label="Artist"
						value={artist}
						onChange={(e) => dispatch(updateForm({ artist: e.target.value }))}
					/>
				</Grid>
				<Grid item>
					<TextField
						fullWidth
						label="Album"
						value={album}
						onChange={(e) => dispatch(updateForm({ album: e.target.value }))}
					/>
				</Grid>
				<Grid item>
					<TextField
						fullWidth
						label="Grouping"
						value={grouping}
						onChange={(e) => dispatch(updateForm({ grouping: e.target.value }))}
						disabled={groupingLoading}
					/>
				</Grid>
			</Grid>
		),
		[album, artist, dispatch, grouping, groupingLoading, title]
	);
};

export default TagInputs;
